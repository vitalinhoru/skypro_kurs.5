from config import config
from utils import add_employer, get_employers, create_database, save_data_to_database
from db_manager import DBManager


def main():
    companies = [
        119069,  # АО "ЗАСЛОН"
        1122462,  # Skyeng
        829983,  # ООО Техномир
        1942330,  # Пятерочка
        1368152,  # ПАО ТАНТК им.Г.М. Бериева
        9187,  # Максидом
        2180,  # Ozon
        3529,  # Сбер
        926498,  # ФК Зенит
        1455  # HeadHunter
    ]
    params = config()  # Параметры из конфига
    database_name = 'companies_db'  # Название БД

    def logic():
        """Запускаем логику программы"""

        per_page = input('Ведите количество вакансий от каждой компании (от 1 до 100):\n'
                         '>>> ')
        if per_page.isalpha() or int(per_page) < 1 or int(per_page) > 100:
            per_page = '10'
            print('Неверное значение. Установлено значение по-умолчанию: 10.\n'
                  '\n'
                  'Получаем данные.')
            data = get_employers(companies, per_page)  # Проверяем корректность ID
            create_database(database_name, params)  # Создаем БД
            save_data_to_database(data, database_name, params)  # Загружаем данные в БД
        else:
            print('\n'
                  'Получаем данные.')
            data = get_employers(companies, per_page)
            create_database(database_name, params)  # Создаем БД
            save_data_to_database(data, database_name, params)

    def db_logic():
        """Работаем с БД через класс"""

        db_m = DBManager(database_name)
        db_num = input('Выберите, что нужно сделать:\n'
                       '1. Получить список всех компаний и количество вакансий у каждой компании\n'
                       '2. Получить список всех вакансий с указанием названия компании, '
                       'названия вакансии и зарплаты и ссылки на вакансию\n'
                       '3. Получить среднюю зарплату по вакансиям\n'
                       '4. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям\n'
                       '5. Получить список всех вакансий, в названии которых содержатся '
                       'переданные в метод слова, например python\n'
                       '>>> ')

        if db_num == '1':
            db_m.get_companies_and_vacancies_count()
        elif db_num == '2':
            db_m.get_all_vacancies()
        elif db_num == '3':
            db_m.get_avg_salary()
        elif db_num == '4':
            db_m.get_vacancies_with_higher_salary()
        elif db_num == '5':
            db_m.get_vacancies_with_keyword()
        else:
            print('Неверный ввод.')

        new_start = input('\n'
                          'Продолжить работу с базой данных?\n'
                          '1. Да\n'
                          '2. Выход\n'
                          '>>> ')
        if new_start == '1':
            db_logic()
        else:
            print('Завершение работы.')

    num = input('Желаете добавить компанию в имеющийся список?\n'
                '1. Да\n'
                '2. Нет\n'
                '3. Посмотреть список имеющихся ID компаний.\n'
                '4. Выход из программы\n'
                '>>> ')
    if num == '1':
        new_id = input('Введите ID компании\n'
                       '>>> ')
        if new_id.isdigit():
            if int(new_id) in companies:
                print('Такой ID уже существует.')
            else:
                add_employer(companies, new_id)
        elif not new_id.isdigit():
            print('Неверный формат. Загружаются данные из списка компаний по-умолчанию.')
        logic()
        db_logic()
    elif num == '2':
        logic()
        db_logic()
    elif num == '3':
        for company in companies:
            print(company)
        print('')
        main()
    elif num == '4':
        print('Завершение работы...')
    else:
        print('Неверная команда.\n'
              '')
        main()


if __name__ == '__main__':
    main()
