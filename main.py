from Ui import *
import Auth
import Tree

def focus(e=None):
    global empty
    if search.get() == "Pretraži..." and empty:
        empty=False
        search.delete(0, tk.END)
        search.config(foreground="White", font=("TkDefaultFont", 9, "normal"))

def unfocus(e=None):
    global empty
    if not search.get():
        empty=True
        search.insert(0, "Pretraži...")
        search.config(foreground="gray", font=("TkDefaultFont", 9, "italic"))

def start():
    global search, tree
    acc = Auth.start()
    if acc == '':
        return -1

    W,H = 1700,850
    board = win('Kontrolna tabla', W, H)
    down = Frame(board, 'bottom', '#222', 'both', False, [W,H-100], [15,15])
    up = Frame(board, 'top', '#161616', 'both', False, [W,60], [15,10])

    try:
        d=Dict2()
        for cls in {Person, Room, Program, Training, Session, Reserve}:
            d[cls.lw()] = load(cls)
        role = "gst" if acc not in d.persons else d.persons[acc].role
    except:
        messagebox.showerror("Greška", "Databaza je korumpirana.")
        return -2
    
    current = None
    buttons = []
    def change(btn, cls, config):
        global tree
        current = cls
        for b in buttons:
            b.config(style='#fff.TButton')
        Style('Accent.TButton', fg= 'black')
        btn.config(style='Accent.TButton')

        tree = Tree.gen(*config)
        filt()
    
    def lbtn(col, title, cls, iff=True):
        if iff:
            btn = Button(up, title, 0, fg=col, bg=col, side='left')
            btn.config(style=f'{col}.TButton', command=lambda: change(btn, cls,  [down,cls,role,acc,d]))
            buttons.append(btn)
    lbtn('#fff','KORISNICI  👤', Person, role in ['su', 'inst'])
    lbtn('#fff','PROGRAMI  📃', Program)
    lbtn('#fff','SALE  🏀', Room, role == 'su')
    lbtn('#fff','TRENINZI  💪🏼', Training, role == 'su')
    lbtn('#fff','TERMINI  🕑', Session)
    lbtn('#fff','REZERVACIJE  📞', Reserve, role != 'gst') 

    Button(up, '➜', lambda :(
        board.destroy(),
        start()
    ), fg="#f00", side='right', bg='red')

    Button(up, '🛈', lambda :(msg(board, """
INFORMACIJE O APLIKACIJI:

Aplikacija se koristi desnim klikom unutar tabele.

Klikom na naziv kolone čija polja mogu uzeti samo
2-3 predefinisane vrednosti će tabelu obojiti
u odnosu na te vrednosti.

Pretraga ispituje sve vrednosti u tabeli
i možete odvojiti više uslova razmakom.
    """)), fg="#03f", side='right', bg='white')

    def exp():
        if msg(board,'Eksportovati trenutnu\ntabelu u fajl?', yn=1):
            export('Log '+str(dt.datetime.now()).replace(':','-'), Tree.get())

    def regen():
        if msg(board,'Generisati termine za\nnarednih 2 nedelje?', yn=1):
            sessgen(d, acc, role)
            filt()

    def lojal():
        if msg(board,'Raspodeliti nagrade lojalnosti?', yn=1):
            users={}
            for p in dv(d.persons):
                if p.role=='reg':
                    users[p.username] = 0
            for r in dv(d.reserves):
                if p.date<now() and p.date>now() - dt.deltatime(days=30):
                    users[r.user] += 1
            for u, n in users.items():
                if n>27:
                    d.persons[u].vip = 1
            save(d.persons, Person)

    if role in {'su','inst'}:
        Button(up, '💾', exp, fg="#0f0", side='right', bg='#0f0')
        Button(up, '⟳', regen, fg="magenta", side='right', bg='magenta')
    if role =='su':
        Button(up, '📃', lambda: izvestaji(board,d), fg="#ff0", side='right', bg='#ff0')
        Button(up, '🏆', lojal, fg="orange", side='right', bg='orange')

    Label(up, 'Gost  ' if acc=='Gost' else f'@{acc}  |  {d.persons[acc].fname} {d.persons[acc].lname}  ').pack(side="right", pady=5)

    L = Label(up, '')
    L.pack(side="right", pady=5)

    Style('TEntry', '#fff', '#444')
    Style('TLabel', '#f2f', '#333')

    srcfrm = Frame(down, "top", '#1c1c1c', 'both', False)
    search = ttk.Entry(srcfrm, style='TEntry')
    search.pack( side="left", fill='both', expand=True, ipady=2, ipadx=2, padx=5, pady=5 )
    unfocus()
    search.bind("<FocusIn>", focus)
    search.bind("<FocusOut>", unfocus)
    extend = tk.BooleanVar()

    def filt(): Tree.redraw([''] if empty else deac(search.get().strip().lower()).split(), extend.get())
    search.bind("<KeyRelease>", lambda event: filt())
    ttk.Checkbutton(srcfrm, variable=extend, command=filt, style = 'aaa.TCheckbutton').pack(side="right", padx=5, pady=5)
    Label(srcfrm, "Šira pretraga", bg='#1d1d1d').pack(side="right", padx=5, pady=5)

    buttons[0].invoke()
    board.mainloop()


if __name__=='__main__':
    start()