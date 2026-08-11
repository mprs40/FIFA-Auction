import json, random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen

PLAYERS=json.load(open("players.json",encoding="utf-8"))

class Auction(Screen):
    def start_game(self):
        self.money=[100,100]; self.teams=[[],[]]; self.used=set(); self.r=0; self.next_round()
    def next_round(self):
        if self.r>=5: return self.finish()
        pos=["حارس","دفاع","وسط","وسط","هجوم"][self.r]
        pool=[p for p in PLAYERS if p["position"]==pos and p["name"] not in self.used]
        self.current=random.choice(pool); self.r+=1
        self.card.text=f"🎲 {self.current["name"]} — {self.current["position"]}\nالجولة {self.r}/5"
        self.info.text=f"💰 {self.names[0]}: {self.money[0]}M | {self.names[1]}: {self.money[1]}M"
        self.b1.text=""; self.b2.text=""
    def bid(self,*args):
        try: a=int(self.b1.text); b=int(self.b2.text)
        except: self.info.text="❌ اكتب المزايدتين"; return
        if a<0 or b<0 or a>self.money[0] or b>self.money[1]: self.info.text="❌ المبلغ أكبر من الميزانية"; return
        if a==b: self.info.text="🤝 تعادل، غيّر المزايدة"; return
        winner=0 if a>b else 1; loser=1-winner; price=max(a,b)
        self.money[winner]-=price; self.teams[winner].append(self.current); self.used.add(self.current["name"])
        pool=[p for p in PLAYERS if p["name"] not in self.used]
        if pool:
            lucky=random.choice(pool); self.used.add(lucky["name"]); self.teams[loser].append(lucky)
            self.info.text=f"🏆 {self.names[winner]} أخذ {self.current["name"]} مقابل {price}M\n🎲 {self.names[loser]} حصل على {lucky["name"]}"
        self.next_round()
    def finish(self):
        def rating(t): return sum(sum(p[k] for k in ["pace","shooting","passing","dribbling","physical","defending"])/6 for p in t)
        r=[rating(self.teams[0]),rating(self.teams[1])]
        g=[max(0,round(r[0]/45+random.uniform(-1,1))),max(0,round(r[1]/45+random.uniform(-1,1)))]
        s=[]
        for team in self.teams:
            names=[p["name"] for p in team if p["position"]!="حارس"]
            s.append(random.sample(names,min(g[len(s)],len(names))))
        w=self.names[0] if g[0]>g[1] else self.names[1] if g[1]>g[0] else "تعادل"
        self.card.text=f"🏆 {w}\n⚽ النتيجة {g[0]} - {g[1]}\n{self.names[0]}: {", ".join(s[0]) or "لا أهداف"}\n{self.names[1]}: {", ".join(s[1]) or "لا أهداف"}"
        self.info.text=f"💰 المتبقي: {self.money[0]}M | {self.money[1]}M"
    def build_ui(self):
        box=BoxLayout(orientation="vertical",padding=15,spacing=8)
        self.info=Label(font_size=17); self.card=Label(font_size=22)
        self.b1=TextInput(hint_text=self.names[0]+" المزايدة",input_filter="int",multiline=False)
        self.b2=TextInput(hint_text=self.names[1]+" المزايدة",input_filter="int",multiline=False)
        go=Button(text="🔨 تأكيد المزايدة",font_size=20); go.bind(on_release=self.bid)
        reset=Button(text="🔄 إعادة"); reset.bind(on_release=lambda x:self.start_game())
        box.add_widget(self.info); box.add_widget(self.card); box.add_widget(self.b1); box.add_widget(self.b2); box.add_widget(go); box.add_widget(reset); self.add_widget(box)

class AppMain(App):
    def build(self):
        self.sm=ScreenManager(); self.menu=Screen(name="menu")
        box=BoxLayout(orientation="vertical",padding=20,spacing=10)
        box.add_widget(Label(text="💰 FIFA AUCTION",font_size=30))
        t1=TextInput(text="محمد",hint_text="الفريق الأول",multiline=False); t2=TextInput(text="معاذ",hint_text="الفريق الثاني",multiline=False)
        go=Button(text="ابدأ المزاد",font_size=22)
        box.add_widget(t1);box.add_widget(t2);box.add_widget(go);self.menu.add_widget(box)
        self.sm.add_widget(self.menu);go.bind(on_release=lambda x:self.start(t1.text,t2.text));return self.sm
    def start(self,a,b):
        s=Auction(name="auction");s.names=[a.strip() or "محمد",b.strip() or "معاذ"];s.build_ui();s.start_game();self.sm.add_widget(s);self.sm.current="auction"
AppMain().run()