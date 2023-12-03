from typing import Any
from config import give_url

import psycopg2
import requests


def check_employer(employer_id):
    """Проверка валидности ID новой компании"""

    url = f'{give_url()}/{employer_id}'
    company_response = requests.get(url)

    if company_response.status_code == 200:
        response = requests.get(url).json()
        return response["name"]


def add_employer(employer_ids: list[int], employer_id: int):
    """Добавляет в список компаний ID новой компании"""

    if check_employer(employer_id):
        print(f'Компания {check_employer(employer_id)} добавлена в список компаний.')
        return employer_ids.append(employer_id)
    else:
        print('Неверный ID. Загружаются данные из списка компаний по-умолчанию.')
        return employer_ids


def get_employers(companies: list[int]):
    """Получаем данные о компаниях через API"""

    employers = []
    params = {
        'page': 0,  # С первой страницы
        'per_page': 10  # Количество
        # 'area': 2  # СПб
    }

    for company in companies:
        url = f'https://api.hh.ru/employers/{company}'
        company_response = requests.get(url).json()  # Инфо о компании
        vacancies_response = requests.get(company_response['vacancies_url'], params).json()  # Вакансии компании
        employers.append({
            'company': company_response,
            'vacancies': vacancies_response['items']
        })
    print('Данные о компаниях получены по API.')

    return employers


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных"""

    conn = psycopg2.connect(dbname='postgres', **params)  # в **params берутся файлы из database.ini
    conn.autocommit = True  # для данного подключения каждый запрос будет коммититься
    cur = conn.cursor()  # курсор

    cur.execute(f'DROP DATABASE IF EXISTS {database_name}')  # сначала удалим, если база была создана с ошибками
    cur.execute(f'CREATE DATABASE {database_name}')

    cur.close()  # закрыли курсор
    conn.close()  # закрыли соединение

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                title varchar(255) NOT NULL,
                company_url varchar(255),
                site_url varchar(255),
                description text
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                company_name varchar(255) NOT NULL,
                company_id INT REFERENCES companies(company_id),
                city VARCHAR(255),
                salary_from int,
                salary_to int,
                vacancy_url VARCHAR(255),
                description text
            )
        """)

    conn.commit()
    conn.close()

    print('База данных создана.')


def check_salary_from(salary):
    """Если нет зарплаты 'от'"""

    if salary is not None:
        return salary['from']
    else:
        return None


def check_salary_to(salary):
    """Если нет зарплаты 'до'"""

    if salary is not None:
        return salary['to']
    else:
        return None


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о каналах и видео в базу данных"""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for company in data:
            company_data = company['company']
            cur.execute("""
                INSERT INTO companies (company_id, title, company_url, site_url, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING company_id
                """,
                        (company_data['id'], company_data['name'], company_data['alternate_url'],
                         company_data['site_url'], company_data['description'])
                        )
            channel_id = cur.fetchone()[0]

            for vacancy in company['vacancies']:
                salary_from = check_salary_from(vacancy['salary'])
                salary_to = check_salary_to(vacancy['salary'])
                cur.execute("""
                    INSERT INTO vacancies (vacancy_id, title, company_name,
                    company_id, city, salary_from, salary_to, vacancy_url, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                            (vacancy['id'], vacancy['name'], vacancy['employer']['name'], channel_id,
                             vacancy['area']['name'],
                             salary_from, salary_to, vacancy['alternate_url'], vacancy['snippet']['responsibility'])
                            )

    conn.commit()
    conn.close()

    print('Данные добавлены.\n'
          '')
