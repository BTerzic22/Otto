import pandas as pd
import numpy as np
import random
import os
import glob


def categories(path):
    """Set categories

    Returns the categorized tab"""
    lexicon = pd.read_excel(path)
    cat = ['adj', 'verb', 'adv', 'gen']
    it = iter(cat)
    for i in range(lexicon.shape[1]):
        if lexicon.iloc[:, i].isna().sum()/lexicon.shape[0] == 1:
            lexicon.iloc[:, i] = next(it)
    return lexicon


def concat(lexicon):
    """Concatenate into 3 columns

    Returns the concatenated tab"""
    salad = pd.DataFrame()
    for i in range(0, lexicon.shape[1], 3):
        tmp = pd.DataFrame(np.array(lexicon.iloc[:, i:i+3]))
        salad = pd.concat([salad, tmp], axis=0, ignore_index=True)

    salad = salad.rename(columns={0: "Category", 1: "German", 2: "French"})
    salad.dropna(inplace=True)
    return salad


def weight(salad):
    """Add a weight column and set it to the mean value

    Returns the weighted tab"""
    weight_list = np.zeros(salad.shape[0])+1.5
    salad["Weight"] = weight_list
    return salad


def index(salad):
    """Index by categories

    Returns the indexed tab
    """
    salad.set_index('Category', inplace=True)
    return salad


def tab_init():
    """Initialize a new tab

    Returns the tab
    """
    path = os.getcwd()+"/Deutsch.xlsx"
    tab = categories(path)
    tab = concat(tab)
    tab = weight(tab)
    tab = index(tab)
    return tab


def user_profile():
    """Defines the user profile. Asks the user to select an existing profile, create a new one or
    automatically generates a new one if there is none.

    Returns the user file name
    -------
    Raises
    ------
    ValueError & TypeError
        If the user enter the wrong command
    """
    os.chdir('Otto')
    file = glob.glob("*.xlsx")
    file.sort(key=os.path.getmtime)
    user_list = list(file)
    print('This is', user_list)
    user_list.remove('Deutsch.xlsx')
    for i in range(len(user_list)):
        user_list[i] = user_list[i].replace('.xlsx', '')

    print("Welcome ! I'm Otto and I will be your smart german trainer.\n")

    if not user_list:
        print("There is no profile registered. Please enter your user name:")
        user_name = input(str())
        tab = tab_init()
        tab.to_excel('{}.xlsx'.format(user_name))
    else:
        print("Do you already have a profile in this list ?\n{}\nYes: 1\nNo: 0".format(
            user_list))
        while True:
            entry = input()
            try:
                entry = int(entry)
                if entry != 0 and entry != 1:
                    raise ValueError
                else:
                    break
            except TypeError:
                print('Please select 0 or 1\n')

            except ValueError:
                print('Please select 0 or 1\n')
        if entry == 0:
            print("Please enter your user name:")
            user_name = input(str())
            tab = tab_init()
            tab.to_excel('{}.xlsx'.format(user_name))
        else:
            print("Please select your user name:")
            while True:
                try:
                    user_name = input(str())
                    if user_name in user_list:
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print('Please type your name again.\n')
    file_name = user_name + ".xlsx"
    return file_name

def language_selection():
    """Allows the user to select the training language.

    Returns both langagues (the one to guess and solution) as strings.
    -------
    Raises
    ------
    ValueError & TypeError
        If the user enter the wrong command
    """
    print("What kind of training do you want ?\nGerman -> French: 0\nFrench -> German: 1\n")
    while True:
        lang = input()
        try:
            lang = int(lang)
            lang_list = ['German', 'French']
            if lang != 0 and lang != 1:
                raise ValueError
            else:
                break
        except TypeError:
            print('Please select a positive integer number of words !\n')
        except ValueError:
            print('Please select a positive integer number of words !\n')
    lang_to_guess = lang_list[lang]
    lang_solution = lang_list[abs(lang-1)]
    return lang_to_guess, lang_solution


def n_words_selection():
    """Allows user to select the number of words to be trained with.

    Returns the number of words to guess a an integer
    -------
    Raises
    ------
    ValueError & TypeError
        If the user enter the wrong command
    """
    print("How much words would you like to find ? Please tape a number\n")
    while True:
        n_words = input()
        try:
            n_words = int(n_words)
            if n_words < 0:
                raise ValueError
            else:
                break
        except TypeError:
            print('Please select a positive integer number of words !\n')
        except ValueError:
            print('Please select a positive integer number of words !\n')
    return n_words


def training_mode():
    """Allows user to choose training mode (whole lexic or by category).

    Returns the the training mode as a string.
    -------
    Raises
    ------
    ValueError & TypeError
        If the user enter the wrong command
    """
    print("\nChoose a training mode:\nA: Adjectives\nV: Verbs\nP: Pronouns & adverbs\nG: General vocabulary\
\nW: Whole lexic")
    cat = ["A", "V", "P", "G", "W"]
    while True:
        mode = input()
        try:
            mode == str(mode)
            mode = str.upper(mode)
            if mode not in cat:
                raise ValueError
            else:
                break
        except TypeError:
            print('Please select the right letter.\n')
        except ValueError:
            print('Please select the right letter.\n')
    return mode


def preprocess_sheet(sheet, mode):
    cat = sheet["Category"].unique()
    dict_cat = {"A": cat[0], "V": cat[1], "P": cat[2], "G": cat[3], "W": "all"}
    if mode != "W":
        r_list = sheet[sheet["Category"] == dict_cat[mode]]
    else:
        r_list = sheet
    mode = dict_cat[mode]
    return r_list, mode


def words_to_guess(n_words, sheet, mode):
    # Set words available by training mode
    r_list, mode = preprocess_sheet(sheet, mode)

    # Initialize the number of words from the lexic
    word_rows = [*range(0, r_list.shape[0])]

    # Choose the words to be tested
    r = random.choices(word_rows, r_list["Weight"], k=n_words)

    # Check if there is no duplicates or replace them
    diff = len(r) - len(set(r))
    while diff != 0:
        r = list(set(r)) #r.drop_duplicates(inplace=True)
        i=0
        while i < diff:
            r.append(random.choices(word_rows, r_list["Weight"], k=1)[0])
            i+=1
        diff = len(r) - len(set(r))
    return r, r_list, mode


def rating_selection(r_number, r_list):
    while True:
        rating = input()
        try:
            rating = int(rating)
            if rating < 0 or rating > 3:
                raise ValueError
            else:
                r_list.iloc[r_number, 3] = (
                    r_list.iloc[r_number, 3] + rating) / 2
                print('\nUnderstood. Danke !')
                break
        except TypeError:
            print("Try again with 0, 1, 2 or 3")
        except ValueError:
            print("Try again with 0, 1, 2 or 3")
    return rating


def guesser(n_words, r, r_list, lang_to_guess, lang_solution):
    n = 0
    session = dict()
    lang_col = {"German": 1, "French": 2}
    guess_col = lang_col[lang_to_guess]
    solution_col = lang_col[lang_solution]
    while n < n_words:
        word = r_list.iloc[r[n], guess_col]
        print('\n#{}/{}: {} : '.format(n+1, n_words, word))
        guess = str(input())
        print("Your answer: {}. Solution: {}.\nHow hard was it ? (0: Sehr einfach, 1: Not perfect, \
2: Quite hard to find, 3: Really missed it)".format(guess, r_list.iloc[r[n], solution_col]))
        session[word] = [r_list.iloc[r[n], solution_col],
                         rating_selection(r[n], r_list)]
        n += 1
    return session


def convert_and_save(r_list, sheet, mode, file_name):
    if mode != "all":
        sheet[sheet["Category"] == mode] = r_list
    else:
        sheet = r_list
    sheet = index(sheet)
    sheet.to_excel(file_name)


def summary(session):
    print("===== End of session. Bis bald ! =====\nHere is your summary:\n")
    for key in session:
        print("Word: {} || Solution: {} || Score: {}".format(
            key, session[key][0], session[key][1]))


def quizz():
    # Select the user tab
    file_name = user_profile()
    sheet = pd.read_excel(file_name)

    # Launch the training
    print("===== Let's start our quizz ! =====\n")
    lang_to_guess, lang_solution = language_selection()
    mode = training_mode()
    n_words = n_words_selection()
    print("Be ready to write the translation of {} the following word(s):".format(n_words))

    # Choose the words to be tested
    r = list()
    r, r_list, mode = words_to_guess(n_words, sheet, mode)

    # Play training session
    session = guesser(n_words, r, r_list, lang_to_guess, lang_solution)

    # Save the modifications in Excel
    convert_and_save(r_list, sheet, mode, file_name)

    # Print the session summary
    summary(session)

if __name__ == "__main__":
    quizz()