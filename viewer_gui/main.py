import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg
from matplotlib.figure import Figure
from pandasql import sqldf
import seaborn as sns
from math import log

#import sqlite3
import tkinter as tk
from tkinter import font  as tkfont
from tkinter import ttk
from tkinter import *
from pandastable import Table, TableModel
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype


lap = pd.read_csv('C:/Users/Николай/Jupyter_projects/saves/mylaps.csv')





root = Tk()

root.title("laptops!")
root.geometry("1800x800")

columns_amount = len(lap.axes[1])

str_columns = [k for k in range(columns_amount) if
               is_string_dtype(lap.iloc[:, k])]

numeric_columns = [k for k in range(columns_amount) if
                   is_numeric_dtype(lap.iloc[:, k])]

# поля ввода
top_frame = tk.Frame(root, height=30, width=1800)
top_frame.pack(side='top')

textBox = []

for k in range(columns_amount):
    ttk.Label(top_frame, text=lap.columns[k]).grid(row=1, column=k + 1)
    textBox.append(ttk.Entry(top_frame))
    textBox[k].grid(row=2, column=k + 1)

# текст label
#label_search_text = 'Configurations for laptops'
#label_search = ttk.Label(top_frame, text=label_search_text).grid(row=3, column=2)

# таблица
table_frame = tk.Frame(root, width=1800)
table_frame.pack(fill='both', expand=True)

pt = Table(table_frame)

pt.model.df = lap

pt.show()


# Кнопки

def button_clear_click():
    for cl in textBox:
        cl.delete(0, 'end')

button_clear = ttk.Button(top_frame, text='Clear',
                           command=button_clear_click).\
                            grid(row=3, column=2)


def button_search_click():
    pt.model.df = lap
    q = 'select * from lap'
    q_add = ''

    # поиск для текстовых
    for k in str_columns:
        if len(textBox[k].get()) != 0:
            q_add = '{} upper({}) like upper(\'%{}%\') and '. \
                format(q_add, lap.columns[k], textBox[k].get())

    #поиск для числовых
    for k in numeric_columns:
        if len(textBox[k].get()) != 0:
            q_add = '{} {} {} and '. \
                format(q_add, lap.columns[k], textBox[k].get())

    if len(q_add) > 0:
        q = q + ' where' + q_add[:-5]
    pt.model.df = sqldf(q)
    pt.show()


button_search = ttk.Button(top_frame, text='Search',
                           command=button_search_click).\
                            grid(row=3, column=1)


def button_stat_click():
    winstat = tk.Toplevel(root)
    winstat.title("statistics")
    winstat.geometry("1600x700")

    stat_top_frame = tk.Frame(winstat, height=30, width=1600)
    stat_top_frame.pack(side='top')

    ttk.Label(stat_top_frame, text=' String values: ').grid(row=1, column=1)
    str_cmb = ttk.Combobox(stat_top_frame, values=lap.columns[str_columns].to_list())
    str_cmb.grid(row=1, column=2)

    ttk.Label(stat_top_frame, text=' Numeric values: ').grid(row=1, column=3)
    num_cmb = ttk.Combobox(stat_top_frame, values=lap.columns[numeric_columns].to_list())
    num_cmb.grid(row=1, column=4)

    def button_refresh_click():
        winstat.destroy()
        button_stat_click()


    button_refresh = ttk.Button(stat_top_frame, text='Refresh',
                             command=button_refresh_click). \
        grid(row=1, column=6)




    def button_show_click():
        chosen_df = pt.model.df
        str_stat = str_cmb.get()
        num_stat = num_cmb.get()

        fig = Figure(figsize=(16, 4), dpi=100)
        donut = fig.add_subplot(131)
        hist_multi = fig.add_subplot(132)
        hist_dist = fig.add_subplot(133)


        #диаграмма столбцы
        try:
            q0 = sqldf('SELECT {0},\
                   count(*) total\
                    from chosen_df\
                    group by {0}\
                    order by count(*) DESC, {0}\
                    LIMIT 2'.format(str_stat))

            # other = pd.DataFrame({'Manufacturer' : 'Other',
            #                            'total' : q['allover'].iloc[0] - q['total'].sum()},
            #                           index=[0])

            # q.drop(['allover'], axis = 1 , inplace = True)
            # q = pd.concat([q,other])

            top1 = q0.iloc[0,0]
            top2 = q0.iloc[1,0]

            qmin = chosen_df[num_stat].min()
            qmax = chosen_df[num_stat].max()
            dot1 = qmin + ((qmax - qmin) / 3.)
            dot2 = 2 * qmin + ((qmax - qmin) / 3.)

            q = sqldf('SELECT \
                    CASE\
                       WHEN {3} < {6} THEN \'1. {4}-{6}\'\
                       WHEN {3} < {7} THEN \'2. {6}-{7}\'\
                       ELSE \'3. {7}-{5}\'\
                    END as q_{3},\
                    CASE\
                        WHEN {0} = \'{1}\' THEN \'{1}\'\
                        WHEN {0} = \'{2}\' THEN \'{2}\'\
                        ELSE \'Other\' \
                    END as q_{0},\
                   count(*) total\
                    from chosen_df\
                    group by q_{0}, q_{3}\
                    order by q_{3}, q_{0}'.format(str_stat, top1, top2, num_stat, qmin, qmax, dot1, dot2))

            mfs = sqldf('SELECT distinct q_{0} from q'.format(str_stat))

            width = 0.3
            #values = np.arange(len(q))
            q_numeric = q['q_'+num_stat].unique()

            values = np.arange(len(q_numeric))
            q1 = q[q['q_'+str_stat] == mfs.iloc[0, 0]]['total'].to_list()
            q2 = q[q['q_'+str_stat] == mfs.iloc[1, 0]]['total'].to_list()
            q3 = q[q['q_'+str_stat] == mfs.iloc[2, 0]]['total'].to_list()

            hist_multi.bar(values-width, q1, width, label=mfs.iloc[0, 0])
            hist_multi.bar(values, q2, width, label=mfs.iloc[1, 0])
            hist_multi.bar(values+width, q3, width, label=mfs.iloc[2, 0])
            hist_multi.legend()
            hist_multi.set_xticks(values, q_numeric)

        except:
            pass






        #круговая диаграмма
        q = sqldf('SELECT {0},\
                           count(*) total,\
                           CAST(100 * sum(count(*)) OVER (ORDER BY count(*) DESC, {0}) as real)\
                               / sum(count(*)) OVER () as cumpercent,\
                           CAST(count(*) * 100 as real)\
                               / sum(count(*)) over()\
                               as percent\
                    from chosen_df\
                    group by {0}\
                    order by count(*) DESC, {0}\
                    '.format(str_stat))

        sumstr = 'Total = ' + q['total'].sum().astype(str)

        other = pd.DataFrame({str_stat: 'Other',
                              'percent': 0},
                             index=[0])

        for k in range(10):

            if q.iloc[k, 2] > 67:
                other['percent'] = 100 - q.iloc[k, 2]
                q = q[:k + 1]
                break
            if k >8:
                other['percent'] = 100 - q.iloc[k, 2]
                q = q[:k + 1]

        q.drop(['total', 'cumpercent'], axis=1, inplace=True)
        q = pd.concat([q, other])

        #гистограмма
        sns.histplot(chosen_df[num_stat], bins=int(log(chosen_df[num_stat].sum(), 2) + 1),
                     ax=hist_dist, color='blue', kde=True, stat="count", linewidth=1)



        donut.pie(q['percent'], wedgeprops=dict(width=0.7),
                      autopct='%1.0f%%', shadow=True, startangle=90, labels = q[str_stat])
        donut.text(0., 0., sumstr, horizontalalignment='center', verticalalignment='center')
        donut.set_title(str_stat, loc = 'center')
        donut.legend(labels = q[str_stat].astype(str) + ' - ' + q['percent'].astype(int).astype(str) + '%', loc="best")
        canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=winstat)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)









    button_show = ttk.Button(stat_top_frame, text='Show results',
                             command=button_show_click). \
        grid(row=1, column=5)





button_stat = ttk.Button(top_frame, text='Statistics',
                           command=button_stat_click).\
                            grid(row=3, column=3)


root.mainloop()