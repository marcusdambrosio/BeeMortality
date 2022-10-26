from selenium import webdriver
import pandas as pd
import numpy as np
import sys, os, time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

def pull():
    url = 'https://research.beeinformed.org/loss-map/'
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    yearDropdown = driver.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div[1]/div[1]/div/div[2]/select')
    selector = Select(yearDropdown)
    element = WebDriverWait(driver, 10).until(EC.element_to_be_selected(selector.options[0]))
    options = selector.options
    names = [c.text for c in options]
    for n in names:
        if n == names[0]:
            pass
        else:
            selector.select_by_visible_text(n)
            time.sleep(2)

        t = driver.find_element_by_tag_name('table').text
        process_table(t, n)




def process_table(table, tname):
    table = table.split('\n')[1:]
    master = pd.DataFrame(columns = ['state', 'loss', 'confidence upper', 'confidence lower', 'beekeepers', 'beek exclusive', 'colonies', 'colonies exclusive'])

    counter = -1
    for t in table:
        counter += 1
        if counter==0:
            state = t.strip()
        elif counter == 1:
            if len(t)>5:
                counter = 0
                continue
            loss = t.replace('%', '').strip()
        elif counter == 2:
            t = t.replace(' - ', '-').strip()
            conf, beek, bexcl, col, colexcl = t.split(' ')
            counter=-1
            master = master.append({'state': state,
                                    'loss': loss,
                                    'confidence upper': conf.split('-')[1].strip(' ').strip('%'),
                                    'confidence lower': conf.split('-')[0].strip(' ').strip('%'),
                                    'beekeepers':beek.strip(),
                                    'bexcl':bexcl.strip(' ').strip('%'),
                                    'colonies': col.strip(),
                                    'colonies exclusive': colexcl.strip(' ').strip('%')}, ignore_index=True)
    master.to_csv(f'mortality_data/{tname.replace("/", "-")}.csv', index=False)

def combine():
    master = pd.DataFrame()
    for file in os.listdir('mortality_data'):
        if 'allyears' in file:
            continue
        currDat = pd.read_csv(f'mortality_data/{file}')
        currDat['year'] = [file.split('-')[0]]*len(currDat)
        master = master.append(currDat)

    master.to_csv('mortality_data/allyears.csv', index = False)

def by_state(state = 'all'):
    data = pd.read_csv('mortality_data/allyears.csv')
    if state != 'all':
        data = data[data['state'] == state]
    else:
        for st in data.groupby('state'):
            st, dat = st
            plt.plot(dat['year'], dat['loss'], label = st)
        plt.legend()
        plt.title('loss vs year (%)')
        plt.show()

        losses = {}
        for st in data.groupby('state'):
            st, dat = st
            losses[st] = dat['loss'].mean()
        losses = {k:v for k,v in sorted(losses.items(), key = lambda item : item[1])}
        plt.bar(losses.keys(), losses.values())
        plt.xticks(rotation = 90)
        plt.title('average loss per state since 2007 (%)')
        plt.show()

        losschange = {}
        for st in data.groupby('state'):
            st, dat = st
            dat.sort_values(by='year', ascending = True, inplace =True)
            losschange[st] = dat.loc[dat.index[-1], 'loss'] - dat.loc[dat.index[0], 'loss']
        plt.bar(losschange.keys(), losschange.values())
        plt.xticks(rotation = 90)
        plt.title('loss change per state since 2007 (%)')
        plt.show()


def lowest_loss():
    data=pd.read_csv('mortality_data/allyears.csv')
    data = data[data['year'] > 2016]
    losses = {}
    for st in data.groupby('state'):
        st,dat=st
        losses[st] = dat['loss'].mean()

    losses = {k: v for k, v in sorted(losses.items(), key=lambda item: item[1])}
    plt.bar(losses.keys(), losses.values())
    plt.xticks(rotation = 90)
    plt.title('average loss per state in last 5 years (%)')
    plt.show()
    losses = list(losses.items())[:10]

    print(losses)

lowest_loss()

