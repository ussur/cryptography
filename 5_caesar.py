import os
import json
from collections import Counter
from nltk import bigrams, trigrams


dir_name = os.path.dirname(__file__)
rus = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
rus_freq = 'оеаинтсрвлкмдпуяыьгзбчйхжшюцщэфъё'


def is_rus(t):
    return all(char in rus for char in t)


def read_file(file_name):
    file_path =  dir_name + '/' + file_name
    with open(file_path, 'r') as file:
        text = file.read()
    return text


def write_file(file_name, text):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(text)


def write_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(sort_by_frequency(data), file,
                  indent=4, ensure_ascii=False)


def sort_by_frequency(counter):
    return dict((''.join(item[0]), item[1]) for item in \
                sorted(counter.items(), key=lambda item: -item[1]))
        
        
def preprocess(text, letters_freq):
    freq_dict = dict(zip(sort_by_frequency(letters_freq).keys(), rus_freq))
    return replace(text, freq_dict)
        
        
def replace(text, freq_dict):
    for char in text:
        if char.lower() in freq_dict:
            new_char = freq_dict[char.lower()]
            if char.istitle():
                new_char = new_char.upper()
        else:
            new_char = char
        yield new_char


if __name__ == "__main__":
    # 1. Read the text from a file
    text = read_file('5_input')
    print('===== SOURCE ====')
    print(text)
   
    # 2. Calculate occurences of letters, bigrams and trigrams
    letters_freq = Counter(char for char in text.lower() if is_rus(char))
    bigrams_freq = Counter(t for t in bigrams(text.lower()) if is_rus(t))
    trigrams_freq = Counter(t for t in trigrams(text.lower()) if is_rus(t))
    
    # include all of the alphabet in letters_freq
    for letter in rus.lower():
        if letter not in letters_freq:
            letters_freq[letter] = 0
    
    # 3. Write the collected statistics to a file
    write_json('output/letters_freq.json', letters_freq)
    write_json('output/bigrams_freq.json', bigrams_freq)
    write_json('output/trigrams_freq.json', trigrams_freq)
    
    # 4. Preprocess the text by matching letter frequences
    preprocessed = ''.join(preprocess(text, letters_freq))
    write_file('output/preprocessed', preprocessed)
    
#    txt_freq = 'тэлрдкювъжьнзибшоефгщпаыухчясйцмё'
#    rus_freq = 'оеаинтсрвлкмдпуяыьгзбчйхжшюцщэфъё'
    
    # 1 iteration
    # плт -> чао -> что (п: ч, л: т, т: о)
    # ьрь -> кик -> как (ь: к, р: а)
    # йлт -> эао -> это (п: э)
    # н -> м -> в ? (м: в)
    # э -> е -> и (часто встречается отдельно) ? (э: и)
    # н -> в -> в (часто встречается отдельно) ? (н: в)
    
    # 2 iteration
    #ореовн -> основе (р: с, е: н, н: е)
    #этиб -> этих (б: х)
    #чтозп -> чтобы (з: б, п: ы)
    #такойо -> такого (й: г)
    
    # 3 iteration
    #есть слово "работает" - тут все буквы правильные
    #коренныл обраяол ияленит -> коренным образом изменит (л: м, я: з)
    #илетп уемо -> иметь дело (п: ь, у: д, м: л)
    #верьт -> верят (ь: я)
    #вягмьуов -> взглядов
    #трауищионныли -> традиционными (у: д, щ: ц)
    #одреуеменныш -> определенный (ш: й)
    
    # 4 iteration
    #гарантиршщт уолншщ невоьможностя -> гарантируют полную невозможность (ш: у, у: п, щ: ю, ь: з, я: ь)
    #уодделки денежных ьнаков -> подделки денежных знаков
    #ншждащтсп -> нуждаются (п: я)
    #уоьволитя -> позволить (я: ь)
    #вьаимоисклщчащфих -> взаимоисключающих (ф: щ)
    
    # new frequency dictionary
    freq_dict = {'т': 'о', # ok
                 'э': 'и', # ok 
                 'л': 'т', # ok
                 'р': 'а', # ok 
                 'д': 'е', # ok
                 'к': 'н', # ok
                 'ю': 'р', # ok
                 'в': 'с', # ok
                 'ъ': 'л', # ok
                 'ж': 'м', # ok
                 'ь': 'к', # ok
                 'н': 'в', # ok
                 'з': 'п', # ok
                 'и': 'ы', # ok
                 'б': 'д', # ok
                 'ш': 'з', # ok
                 'о': 'ь', # ok
                 'е': 'я', # ok
                 'ф': 'у', # ok
                 'г': 'б', # ok
                 'щ': 'х', # ok
                 'п': 'ч', # ok
                 'а': 'г', # ok
                 'ы': 'ю', # ok
                 'у': 'ж', # ok
                 'х': 'й', # ok
                 'ч': 'ф', # ok
                 'я': 'ш', # ok
                 'с': 'ц', # ok
                 'й': 'э', # ok
                 'ц': 'щ', # ok
                 'м': 'ъ', # ok
                 'ё': 'ё'} # ok
    
    # 5. Output deciphered text 
    deciphered = ''.join(replace(text, freq_dict))
    print('===== DECIPHERED ====')
    print(deciphered)
    write_file('output/deciphered', deciphered)
    