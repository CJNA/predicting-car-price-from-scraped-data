import os
path = '/Users/cjna/Desktop/Src/predicting-car-price-from-scraped-data/picture-scraper/'

os.chdir(path)

directory = '/Users/cjna/Desktop/Src/predicting-car-price-from-scraped-data/picture-scraper/image'

# files = ['scrape', 'tag']
files = ['save', 'select_images']

if __name__ == '__main__':
    if not os.path.isdir(directory):
        os.mkdir(directory)

    [os.system('python ' + path + f'{file}.py ' + directory) for file in files]
