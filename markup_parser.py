class MarkupParser:
    def __init__(self):
        pass
        
    def parse_markup_file(self, file_path):
        """Парсит файл разметки и возвращает данные в формате [(class_id, [(x1, y1), (x2, y2), ...]), ...]"""
        markup_data = []
        
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    values = line.strip().split()
                    if len(values) > 1:
                        class_id = int(values[0])
                        points = []
                        for i in range(1, len(values), 2):
                            if i+1 < len(values):
                                x = float(values[i])
                                y = float(values[i+1])
                                points.append((x, y))
                        markup_data.append((class_id, points))
                        
            return markup_data
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла разметки: {e}")