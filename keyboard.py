
#%matplotlib inline
from enum import Enum
import itertools
#import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import seaborn_image as sbi
import seaborn_image as isns
import functools
from matplotlib.colors import LinearSegmentedColormap
#import pylustrator

class Row(Enum):
    Number = 0
    Top=1
    Home=2
    Bottom=3
    Space = 4
class Finger(Enum):
    Thumb = 0
    Pinky=1
    Ring=2
    Finger=3
    Index = 4
    Index_inner = 5
class Hand(Enum):
    Left=1
    Right=2
    Sp=3

class Row_infos():
    r0=r"1234567890-="
    r1=r"qwertyuiop[]"
    r2="asdfghjkl;'\\"
    r3=r"zxcvbnm,./"
    r4 =" "
    s0=r"!@#$%^&*()_+"
    s1=r"QWERTYUIOP{}"
    s2="ASDFGHJKL:\"|"
    s3=r"ZXCVBNM<>?"
    all_unshifted = [r0,r1,r2,r3]
    all_shifted = [s0,s1,s2,s3]
    
    rowstarts = [60,90,105,135,239]
    cell_size = 60


    @staticmethod
    def get_key_info():
        if Row_infos.key_info:
            return Row_infos.key_info
        concat = lambda arr:itertools.chain.from_iterable(arr)
        get_row_ord = lambda arr:concat([list(map(lambda _:i, arr[i])) for i in range(len(arr))])
        finger_ord_f = lambda r:list(map(Finger,[1,2,3,4,5,5,4,3,2,1,1,1,1][:len(r)]))
        hand_ord_f = lambda r: list(map(Hand,[1,1,1,1,1,2,2,2,2,2,2,2,2][:len(r)]))
        apply_to_rows = lambda f,rs:f(rs[0])+f(rs[1])+f(rs[2])+f(rs[3])

        finger_ord = apply_to_rows(finger_ord_f,Row_infos.all_unshifted)
        hand_ord = apply_to_rows(hand_ord_f,Row_infos.all_unshifted)
        row_ord = get_row_ord(Row_infos.all_unshifted)

        key_info = {}
        for s,us,f,h,r in \
            zip(concat(Row_infos.all_shifted),concat(Row_infos.all_unshifted),finger_ord,hand_ord,row_ord):
            
            key_info[s] = (f,h,r)
            key_info[us] = (f,h,r)
        key_info[' '] = (Finger.Thumb,Hand.Sp,Row.Space)
        Row_infos.key_info = key_info
        return key_info



def extract_avg_latency (dict, chr_s,chr_us):
    occ1,avg1 = dict[chr_s]
    occ2,avg2 = dict[chr_us]
    return 0 if occ1+occ2 == 0 else avg1 * (occ1/(occ1+occ2)) + avg2 * (occ2/(occ1+occ2))

def extract_occurances (dict, chr_s,chr_us):
    occ1,avg1 = dict[chr_s]
    occ2,avg2 = dict[chr_us]
    return occ1+occ2

def get_heatmap(data_dict,extract_item=extract_avg_latency,normalise=9,normalise_f=None):
    
    #extract_item = functools.partial(data_f,)
    shape = (900,300)
    img = np.zeros(shape)
    cell_size = Row_infos.cell_size
    empty_cell = np.zeros([cell_size,cell_size])
    vals = []
    for i,(row_s,row_us) in enumerate(zip(Row_infos.all_shifted,Row_infos.all_unshifted)):
        x_offset = Row_infos.rowstarts[i]
        row_y_start = shape[1] - i*cell_size 
        x_empty_from = x_offset+len(row_s)*cell_size
        
        row_img = [(extract_item(data_dict,chr_s,chr_us))/normalise for (chr_s,chr_us) in zip(row_s,row_us)]
        for val in row_img:
            vals.append(val)
        row_img = [empty_cell+val for val in row_img]
        row_img = np.concatenate(row_img,0)
        img[x_offset:x_empty_from,row_y_start-cell_size:row_y_start] = row_img
    if normalise_f:
        vals.sort()
        img=normalise_f(vals,img)
    return img

def apply_colormap(img,colormap):
    cmap = cm.get_cmap('viridis').__call__()
    aaa = np.vectorize(cmap)(colormap)
    bbb = np.where(img>200,img,colormap)
    return bbb
def show_heatmap(data_dict,extraction_f,alpha=0.8,normalise_f=None):
        #fig,ax = start_plot()
        #ax.invert_yaxis()
        # divider = make_axes_locatable(ax)
        # cax = divider.append_axes('right', size='5%', pad=0.05)
        img = 1-plt.imread('qwerty.png')[::-1,...]
       

        # image with a scalebar
        #plt.figure(figsize=(15,42))
        isns.set_context("paper")

        # change image related settings
        #isns.set_image(cmap=None, despine=True)  # set the colormap and despine the axes
        #isns.set_scalebar(color="red")
        #extent = np.min(x[]), np.max(x), np.min(y), np.max(y)
        #fig = plt.figure(frameon=False)
        fig, ax = plt.subplots()
        plt.xticks([])
        plt.yticks([])
        ax.axis('off')
        heatmap = get_heatmap(data_dict,extract_item=extraction_f,normalise_f=normalise_f)
        b = cm.get_cmap('binary')(img) 
        h= cm.get_cmap('Oranges')(heatmap.T/np.max(heatmap),alpha=1)
        im = np.where(b<0.5,b,h)
        ax.imshow(im,interpolation='antialiased')
        # im1 = ax.imshow(img, cmap=plt.cm.binary,interpolation='antialiased')
        # im2 = ax.imshow(heatmap.T, cmap='Oranges',alpha=0.8,interpolation='antialiased')
        #plt.setp(im1, zorder=0)
        #plt.setp(im2, zorder=1)
        #ax.figure.siz
        #isns.imgplot(img,cmap='red',describe=True,ax=ax,zorder=0,alpha=0.3)
        #ax2.invert_yaxis()
        # plt.setp(ax2, zorder=100)
        #ax.invert_xaxis()
        #ax.imshow(img, zorder=0)#,extent=[0, 101,300, 0])
        mng = plt.get_current_fig_manager()
        #mng.window.state('zoomed')
        plt.show()

def zerozero(): return (0,0)

if __name__ == '__main__':
    import scraper
    df,key_freq = scraper.load_mined()
    show_heatmap(key_freq,extract_avg_latency)