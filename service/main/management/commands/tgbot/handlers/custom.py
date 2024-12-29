from aiogram.filters.callback_data import CallbackData


# Создаем класс для callback_data
class CustomCallbackData(CallbackData):
    def __init__(self, action: str, id: int, callback_data: str = None):
        # Вызываем родительский конструктор
        super().__init__('faq', 'action', 'id', 'callback_data')

        # Инициализация атрибутов
        self.action = action
        self.id = id
        self.callback_data = callback_data if callback_data else ""

    # Метод для упаковки данных в строку
    def pack(self):
        return super().pack(action=self.action, id=self.id, callback_data=self.callback_data)

    # Метод для распаковки строки обратно в объект
    @classmethod
    def unpack(cls, data: str):
        unpacked_data = super().unpack(data)
        return cls(
            action=unpacked_data['action'],
            id=unpacked_data['id'],
            callback_data=unpacked_data['callback_data']
        )


# Пример использования:
faq_data = CustomCallbackData(action="details", id=1, callback_data="sample_callback_data")

# Получение упакованной строки для callback_data
callback_data_string = faq_data.pack()
print(callback_data_string)  # Выводит строку для callback_data

# Распаковка строки обратно в объект
unpacked_faq_data = CustomCallbackData.unpack(callback_data_string)
print(unpacked_faq_data.action)  # Выводит 'details'
print(unpacked_faq_data.id)  # Выводит 1
print(unpacked_faq_data.callback_data)  # Выводит 'sample_callback_data'
