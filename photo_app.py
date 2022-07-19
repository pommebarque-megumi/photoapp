"""
https://algorithm.joho.info/programming/python/opencv-manga-camera-py/
画像加工は上記のサイトを参考にさせてもらいました。
ありがとうございます。
"""
import cv2
import numpy as np
import tkinter as tk
import tkinter.messagebox as mbox
from PIL import Image,ImageFilter,ImageOps,ImageTk

root = tk.Tk()
root.title('写真を加工しよう♪')
root.geometry('400x600')
bg = tk.PhotoImage(file='images/photoappBG.png')
bgLabel = tk.Label(root,image=bg)
bgLabel.pack()

#photo processing(加工)種類数
pp_num = 10
pp_type = ['pen','clasic','mono','comic','wakeup','emboss','defolme','horror','night','cheki']
#pp_photos = []#加工済み画像用リスト

#IntVar & RadioButton
rbtn=[None]*pp_num
radiobt_text = ['ペン画風','クラシカルアート','モノトーン','オールドコミック','目覚めると','エンボス','デフォルメ','ホラー','キラキラ夜空','チェキ風']
var = tk.IntVar()
var.set(0)
btnoffset = (40*pp_num+1)+140
xoffset = 30
    
for i in range(pp_num):
    rbtn[i] = tk.Radiobutton(root,value=i,variable=var,text=radiobt_text[i],fg='#444',bg='#fffabc')
    rbtn[i].place(x=xoffset,y=140+40*i)


imglabel = tk.Label(text='加工したい画像の名前を拡張子を含めて入力してください',fg='#444',bg='#fffabc')
imgentry = tk.Entry(width=30)
imglabel.place(x=xoffset,y=20)
imgentry.place(x=xoffset,y=50)
photo_type_label = tk.Label(text='どのように加工するか選んでください',fg='#444',bg='#fffabc')
photo_type_label.place(x=xoffset,y=100)


"""
ここからfnction & btn宣言
"""

def sub_color(src,K):
    #次元数を１落とす
    Z = src.reshape((-1,3))

    #float32型に変換
    Z = np.float32(Z)

    #基準の定義
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)

    #K-means法で減色
    ret,label,center = cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

    #UNIT8に変換
    center = np.uint8(center)
    res = center[label.flatten()]

    #配列の次元数と入力画像と同じに戻す
    return res.reshape((src.shape))


#ここからペン画化function
def anime_filter(img,K):
    #グレースケール変換
    gray = cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)

    #ぼかしでノイズ低減
    edge = cv2.blur(gray,(3,3))

    #Cannyアルゴリズムで輪郭抽出
    edge = cv2.Canny(edge,50,150,apertureSize=3)

    #輪郭抽出をRGB空間に変換
    edge = cv2.cvtColor(edge,cv2.COLOR_GRAY2BGR)

    #画像の領域分割
    img = sub_color(img,K)

    #差分を返す
    return cv2.subtract(img,edge)



#クラシカル用function
def mosaic(img,alpha):
    #画像の高さ、幅、チャンネル度
    h,w,ch = img.shape

    #縮小⇨拡大でモザイク加工
    img = cv2.resize(img,(int(w*alpha),int(h*alpha)))
    img = cv2.resize(img,(w,h),interpolation=cv2.INTER_NEAREST)

    return img


def pixel_art(img,alpha=2,K=4):
    #モザイク処理
    img = mosaic(img,alpha)

    #減色処理
    return sub_color(img,K)




#(できるか微妙…)完了　モノトーン用function
def monotone(img):
    return cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)


#コミック
def manga_filter(src,screen,th1=60,th2=150):
    #グレースケール変換
    gray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    screen = cv2.cvtColor(screen,cv2.COLOR_BGR2GRAY)

    #スクリーントーン画像を入力画像と同じサイズに
    screen = cv2.resize(screen,(gray.shape[1],gray.shape[0]))
    
    #Cannyアルゴリズムで輪郭検出・色反転
    edge = 255-cv2.Canny(gray,80,120)

    #三値化
    gray[gray <= th1] = 0
    gray[gray >= th2] = 255
    gray[np.where((gray > th1)&(gray < th2))] = screen[np.where((gray >th1)&(gray < th2))]

    return cv2.bitwise_and(gray,edge)
    

#キラキラ夜空
def night(pil_img):
    im_back = Image.open('images/universe.jpg').resize(pil_img.size)
    mask_im = Image.open('images/m_universe.jpg').resize(pil_img.size).convert('L')
    result = im_back.copy()
    result.paste(pil_img,(0,0),mask_im)

    return result


#チェキ風
def cheki(pil_img):
    width = pil_img.size[0]
    height = pil_img.size[1]
    w_offset = (width/2)-(height/2)
    h_offset = (height/2)-(width/2)

    bg_cheki = Image.open('images/cheki.jpg')

    if width > height:
        cheki = pil_img.crop((w_offset,0,height+w_offset,height))
    else:
        cheki = pil_img.crop((0,h_offset,width,width+h_offset))

    r_cheki = cheki.resize((364,364))
    result = bg_cheki.copy()
    result.paste(r_cheki,(31,37))

    return result

imgname = None

#ボタンがクリックされた時
def click_btn():
    photoType = var.get()
    imgname = imgentry.get()
    #file名がなかった時のmessageBox
    if not len(imgname) == 0:
        try:
            #入力画像の読み込み
            screen = cv2.imread('images/screen.png')
            cv_img = cv2.imread('images/'+imgname)
            pil_img = Image.open('images/'+imgname)

            if photoType == 0:
                newImg = anime_filter(cv_img,30)
            elif photoType == 1:
                newImg = pixel_art(cv_img,0.5,4)
            elif photoType == 2:
                newImg = monotone(cv_img)
            elif photoType == 3:
                newImg = manga_filter(cv_img,screen,70,140)
            elif photoType == 4:
                newImg = pil_img.filter(filter = ImageFilter.BLUR)
            elif photoType == 5:
                newImg = pil_img.filter(filter = ImageFilter.EMBOSS)
            elif photoType == 6:
                newImg = pil_img.filter(filter = ImageFilter.MinFilter())
            elif photoType == 7:
                newImg = ImageOps.invert(pil_img)
            elif photoType == 8:
                newImg = night(pil_img)
            else:
                newImg = cheki(pil_img)

            #結果出力・保存
            newImgPath = f'images/{pp_type[photoType]}_{imgname}'
            #pp_photos.append(newImgPath)#加工した画像のパスをリストに追加
    
            if photoType < 4:
                cv2.imwrite(newImgPath,newImg)
            else:
                newImg.save(f'images/{pp_type[photoType]}_{imgname}')

            new_pil_img = Image.open(newImgPath)
            new_pil_img.show()
        except FileNotFoundError:
            mbox.showinfo('!!','ファイル名またはファイルの場所が違います')
    else:
        mbox.showinfo('!!','フィル名を入力してください')

btn=tk.Button(text='加工する',command=click_btn,fg='#444',bg='#fffabc')
btn.place(x=xoffset,y=btnoffset)


"""
#保存した画像をデジタルフォトフレーム風に表示したい
index=0
test_pp = ['images/sample01.jpg','images/flowers01.jpg','images/tamagawa.jpg']
def show_pp_photos():
    global index

    show_root = tk.Tk()
    show_root.title('加工済み画像')
    show_canvas = tk.Canvas(width=800,height=800)
    show_canvas.pack()

    ppimg = Image.open(test_pp[index % len(test_pp)])
    tkimg = ImageTk.PhotoImage(ppimg)

    show_canvas.delete('PIC')
    show_canvas.create_image(400,400,image=tkimg,tag='PIC')

    index += 1

    root.after(3000,show_pp_photos)

show_btn = tk.Button(text='加工した画像を見る',command=show_pp_photos,fg='#444',bg='#fffabc')
show_btn.place(x=xoffset*6,y=btnoffset)
"""

root.mainloop()

