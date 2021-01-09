import argparse
import os
import requests
import re
import smtplib
import time
import yaml
from bs4 import BeautifulSoup as bs
from email.message import EmailMessage


def get_config(path=os.getcwd()+'\config.yaml'):
    """[Get the required informations from config]

    Args:
        path (optional): [path of the config file or it gets the 'config.yaml' file in the same directory]

    """
    with open(path, 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
        
        urls= [key for key in config['Product'].keys()]
        target_prices=[float(value) for value in config['Product'].values()]
        
        if len(urls) != len(target_prices):
            print(f'Number of the elements in url and target price are different')
        
        sender=config['Sender'].get('email')
        password=config['Sender'].get('password')
        
        receiver=config['Receiver'].get('email')
        
        
    
    return urls, target_prices, sender, password, receiver, config

def get_price(url):
    """[Scrape the product's informations(price and name)]

    Args:
        url ([str]): [url of the product page]

    Returns:
        [float, str]: [Price and Name of the product]
    """
    r = requests.get(url)
    soup = bs(r.content, features='html.parser')
    
    try:
        price_section1 = soup.select_one('span.prc-slg').string
        possible_price1 = list(map(int, re.findall('\d+', price_section1)))[0]
        
        price_section2 = soup.select_one('span.prc-dsc').string
        possible_price2 = list(map(int, re.findall('\d+', price_section2)))[0]
        
    except:
        price_section = soup.select_one('span.prc-slg').string
        price = list(map(int, re.findall('\d+', price_section)))[0]
    else:
        price=min(possible_price1, possible_price2)
    finally:
        product_name = soup.select_one('h1.pr-new-br').get_text()
    
    return price, product_name

def send_mail(url, sender, password, receiver, product_name, target_price):
    """[All message info and sending mail]

    Args:
        url ([str]): [url of the product page]
        sender ([str]): [Email of the sender]
        password ([str]): [Password of the sender]
        receiver ([str]): [Email of the receiver]
        product_name ([str]): [Name of the product]
        target_price ([float]): [Threshold price: Send email lower than this price]
    """
    msg = EmailMessage()
    msg['Subject'] = 'Price is dropped'
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(f'Price of the {product_name} is down to {target_price}\nHere is the link: {url}')
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        
        smtp.send_message(msg)



def Tracker():
    """[Tracker function that pulls everything together]
    """
    parser = argparse.ArgumentParser(description='Trendyol Price Tracker')
    parser.add_argument('-p','--path', type=str, help='Path of the config file')
    parser.add_argument('-i','--indefined', default=False, type=bool, help='If specified, works until there is nothing to track')
    args =parser.parse_args()
    
    if args.path:
        urls, target_prices, SENDER, PASSWORD, RECEIVER, config = get_config(args.path)
    else:
        urls, target_prices, SENDER, PASSWORD, RECEIVER, config = get_config()
    
    
    prices=[]
    product_names=[]
    for url in urls:
        price, product_name = get_price(url)
        prices.append(price)
        product_names.append(product_name)
        time.sleep(1)
    
    info_dict={}
    for url, product_name, price, target_price in zip(urls, product_names, prices, target_prices):
        info_dict[url]=[product_name, price, target_price]

    while True:
        urls_to_delete=[] #list of the urls that will be deleted every loop
        
        for key, value in info_dict.items():
            if value[1] < value[2]:
                #print(value[1] , value[2]) to understand if it isworking right
                send_mail(key, SENDER, PASSWORD, RECEIVER, value[0], value[2])
                urls_to_delete.append(key)
        
        if urls_to_delete:
            for i in urls_to_delete:
                info_dict.pop(i)
                config['Product'].pop(i)
            
            if args.path:
                with open(args.path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            else:
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                    
        
        if len(info_dict)==0 or not args.indefined:
            break            
        time.sleep(60*60)       
        
if __name__ == '__main__':
    Tracker()