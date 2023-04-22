import pygame
import time
import serial

class Judgetext:
    def __init__(self, number, combo, lane):
        self.num = number
        self.lane = lane
        self.font = pygame.font.SysFont(None, 50)
        if(number == 0):
            self.text = "perfect"
        elif(number == 1):
            self.text = "great"
        elif(number == 2):
            self.text = "good"
        elif(number == 3):
            self.text = "miss"
        else:
            self.text = ""
        self.starttime = time.time()
        if(combo > 0):
            self.text += " {0}".format(combo)

    def Count_time(self):
        if(time.time() - self.starttime > 1):
            self.text = ""

    def Blit(self, screen):
        self.judgetext = self.font.render(self.text, True, (0,0,0))
        screen.blit(self.judgetext, (256 * (note.lane - 1), 670))

class Note:
    def __init__(self, speed, lane):
        self.speed = speed
        self.lane = lane
        self.x = (lane - 1) * 256 + 1
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, 255, 50)

    def Move(self):
        self.rect = self.rect.move(0, self.speed)
        self.error = abs( ((self.rect.top + self.rect.bottom) / 2) - 650 )

    def Judge(self):
        if(self.error < 60 * 0.05 * self.speed):
            #perfect
            return 0
        elif(self.error > 60 * 0.05 * self.speed and self.error < 60 * 0.15 * self.speed):
            #great
            return 1
        elif(self.error > 60 * 0.15 * self.speed and self.error < 60 * 0.25 * self.speed):
            #good
            return 2
        else:
            #miss
            return 3

#pygameの初期設定
pygame.init()
screen = pygame.display.set_mode((1280,720))
running = True
clock = pygame.time.Clock()
bgcolor = pygame.Color(200,200,200)
linecolor = pygame.Color(0,0,0)

#ゲームの設定
note = Note(6, 3)
notes = []
notes.append(note)
text = Judgetext(-1, 0, 3)   #テキストの初期化
combo = 0

#シリアル通信の設定
ser = serial.Serial('COM3', 9600, timeout=0.1)
ser_value = 0   #シリアル通信の値 0:押されていない 1:押されている
ser_value_last = 0   #1回前のシリアル通信の値 0:押されていない 1:押されている
buttonstate = 0   #0:押されてない 1:押された 2:継続して押されている

while running:

    #ゲーム終了の設定
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #ゲーム画面の描画
    screen.fill(bgcolor)
    pygame.draw.line(screen, linecolor, pygame.Vector2(256,0), pygame.Vector2(256,720), width = 1)
    pygame.draw.line(screen, linecolor, pygame.Vector2(512,0), pygame.Vector2(512,720), width = 1)
    pygame.draw.line(screen, linecolor, pygame.Vector2(768,0), pygame.Vector2(768,720), width = 1)
    pygame.draw.line(screen, linecolor, pygame.Vector2(1024,0), pygame.Vector2(1024,720), width = 1)
    pygame.draw.line(screen, linecolor, pygame.Vector2(0,650), pygame.Vector2(1280,650), width = 1)

    #シリアル通信を受信してボタンの状態を取得
    # keys = pygame.key.get_pressed()
    data = ser.read_all()   #送信されたデータを取得
    if(len(data.decode()) != 0):
        ser_value = int( data[len(data.decode()) - 1] )   #送信されたデータの最後を取得
        #ボタンの状態を判定
        if(ser_value == 1 and ser_value_last == 0):
            buttonstate = 1
        elif(ser_value == 1 and ser_value_last == 1):
            buttonstate = 2
        else:
            buttonstate = 0
        
        ser_value_last = ser_value

    #ノーツの判定を行う
    for n in notes:

        n.Move()
        pygame.draw.rect(screen, 'red', n.rect, width=0)

        # if(keys[pygame.K_SPACE]):   #スペースキー押されたとき
        if(buttonstate == 1):   #ボタン押されたとき
            if(note.error < 60 * 0.35 * note.speed):
                if(note.Judge() < 3):   #miss以外
                    combo += 1
                else:
                    combo = 0
                text = Judgetext(note.Judge(), combo, 3)
                notes.clear()
                note = Note(6,3)
                notes.append(note)

        if(note.rect.top >= 650 + 60 * 0.25 * note.speed):
            combo = 0
            text = Judgetext(note.Judge(), combo, 3)
            notes.clear()
            note = Note(6,3)
            notes.append(note)

    #テキストに関する判定
    text.Count_time()
    text.Blit(screen)

    #画面の更新
    pygame.display.flip()

    clock.tick(60)   #1秒に60フレーム

pygame.quit()