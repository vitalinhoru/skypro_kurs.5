import psycopg2
from config import config


class DBManager:

    def __init__(self, database_name):
        self.database_name = database_name
        params = config()
        self.params = params

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании."""
        conn = psycopg2.connect(database=self.database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT companies.title, count(vacancies.vacancy_id)\n'
                                'FROM companies\n'
                                'INNER JOIN vacancies USING(company_id)\n'
                                'GROUP BY company_id')
                    rows = cur.fetchall()
                    print('Список всех компаний и количество вакансий у каждой компании:')
                    for row in rows:
                        print(row)
        finally:
            conn.close()

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании, названия
        вакансии и зарплаты и ссылки на вакансию."""
        conn = psycopg2.connect(database=self.database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT company_name, title, (salary_from + salary_to)/2 AS salary, vacancy_url\n'
                                'FROM vacancies')
                    rows = cur.fetchall()
                    print('Все вакансии: название компании, название вакансии, средняя зарплата, ссылки на вакансию:')
                    for row in rows:
                        print(row)
        finally:
            conn.close()

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям."""
        conn = psycopg2.connect(database=self.database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT title, (salary_from + salary_to)/2 AS salary\n'
                                'FROM vacancies')
                    rows = cur.fetchall()
                    print('Название вакансии, средняя зарплата:')
                    for row in rows:
                        print(row)
        finally:
            conn.close()

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше
        средней по всем вакансиям."""
        conn = psycopg2.connect(database=self.database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute('select title, (salary_from + salary_to)/2 AS salary, vacancy_url\n'
                                'from vacancies\n'
                                'where (salary_from + salary_to)/2 > (select AVG((salary_from + salary_to)/2) from vacancies)')
                    rows = cur.fetchall()
                    print('Cписок всех вакансий, у которых зарплата выше средней по всем вакансиям:')
                    for row in rows:
                        print(row)
        finally:
            conn.close()

    def get_vacancies_with_keyword(self):
        """Получает список всех вакансий, в названии которых содержатся
        переданные в метод слова, например python."""
        query = input('Введите ключевое слово для поиска:\n'
                      '>>> ')
        conn = psycopg2.connect(database=self.database_name, **self.params)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(f"select title, (salary_from + salary_to)/2 AS salary, vacancy_url\n"
                                f"from vacancies\n"
                                f"where lower(title) like '{query}%' or lower(title) like '%{query}' or lower(title) like '%{query}%'")
                    rows = cur.fetchall()
                    print('Список всех вакансий, в названии которых содержатся переданные в метод слова:')
                    for row in rows:
                        print(row)
        finally:
            conn.close()
