import configparser


class Information:

    def __init__(self):
        self.DB_HOST = ''
        self.DB_NAME = ''
        self.DB_PORT = ''
        self.DB_USERNAME = ''
        self.DB_PASSWORD = ''
        self.config = configparser.ConfigParser()

    def start(self):
        end = False
        while not end:
            self.get_values()
            print(self.get_settings(), end='')
            end = self.confirm()

    def get_values(self):
        self.DB_HOST = input('Введите host базы данных [localhost]: ')
        self.DB_HOST = self.DB_HOST or 'localhost'
        self.DB_NAME = input('Введите название базы данных: ')
        self.DB_PORT = input('Введите port [3306]: ')
        self.DB_PORT = self.DB_PORT or '3306'
        self.DB_USERNAME = input('Ввeдите username: ')
        self.DB_PASSWORD = input('Введите пароль: ')

    def set_values_to_file(self):
        self.config.add_section('Database')
        self.config.set('Database', 'DB_HOST', self.DB_HOST)
        self.config.set('Database', 'DB_NAME', self.DB_NAME)
        self.config.set('Database', 'DB_PORT', self.DB_PORT)
        self.config.set('Database', 'DB_USERNAME', self.DB_USERNAME)
        self.config.set('Database', 'DB_PASSWORD', self.DB_PASSWORD)
        self.write_settings()

    def write_settings(self):
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

    def get_settings(self):
        return f"\nВы ввели:\n" \
               f"DB_HOST = {self.DB_HOST}\n" \
               f"DB_NAME = {self.DB_NAME}\n" \
               f"DB_PORT = {self.DB_PORT}\n" \
               f"DB_USERNAME = {self.DB_USERNAME}\n" \
               f"DB_PASSWORD = {self.DB_PASSWORD}\n"

    def confirm(self):
        while True:
            value = input(f"Подтвердить действие? [Y/N]: ").upper()
            if value == 'Y':
                self.set_values_to_file()
                return True
            elif value == 'N':
                return False


if __name__ == '__main__':
    hue = Information()
    hue.start()