NO = mapa.cid("Norway")
NOG = (9.5, 61.5)
EKO = (3.2, 56.55)
DARK = (40, 40, 40)

# L0 gancho: mapa → Noruega, luego dinero
cut(0.0, mapbg((14, 56, 22), (11, 62, 42), {NO: RED}), sfx=None)
sfx(0.0, "impact", 0.8); sfx(0.0, "whoosh", 0.6)
ov(0.2, "ring", geo=NOG)
cut(tw(0, "millonario"), photo(P("money_0"), 1.15, 1.0), sfx="whoosh_fast")
ov(tw(0, "millonario"), "title", text="¿MILLONARIOS?", color=YEL, y=340, size=130); sfx(tw(0, "millonario"), "coins", 0.9)
# L1 y decidió no hacerlo
ov(tw(1, "decidio"), "stamp", text="DECIDIÓ QUE NO", color=RED, y=860); sfx(tw(1, "decidio"), "stamp", 1.0)
ov(tw(1, "decidio"), "shake", dur=0.4)
# L2 Es Noruega / guardó su petróleo
cut(tw(2), photo(P("fjord_0"), 1.12, 1.0, (0.5, 0.45), (0.5, 0.55)))
ov(tw(2, "noruega"), "title", text="NORUEGA", color=WHITE, box=RED, y=420, size=130); sfx(tw(2, "noruega"), "pop", 0.8)
cut(tw(2, "guardo"), photo(P("oilrig_2"), 1.0, 1.12), sfx="whoosh_fast")
ov(tw(2, "guardo"), "title", text="GUARDÓ SU|PETRÓLEO", color=YEL, y=340); sfx(tw(2, "guardo"), "coins", 0.7)
# L3 años 60: pescadores, de los más pobres
cut(tw(3), photo(P("fishing_1"), 1.0, 1.12))
ov(tw(3, "60"), "tag", text="AÑOS 60", y=330, color=WHITE, bg=DARK); sfx(tw(3, "60"), "pop", 0.7)
ov(tw(3, "pescadores"), "title", text="PESCADORES|Y BARCOS", color=WHITE, box=(52, 152, 219), y=460)
cut(tw(3, "pobres"), photo(P("lofoten_3"), 1.12, 1.0), sfx="whoosh_fast")
ov(tw(3, "pobres"), "title", text="DE LOS MÁS POBRES|DE EUROPA OCCIDENTAL", color=WHITE, box=DARK, y=340, size=96)
# L4 1969: Ekofisk en el Mar del Norte
cut(tw(4), mapbg((8, 59, 40), (4.5, 57.3, 95), {NO: RED}))
ov(tw(4), "counter", a=1950, b=1969, dur=0.6, y=330); sfx(tw(4), "pop", 0.6)
ov(tw(4, "norte"), "label", text="MAR DEL NORTE", geo=(1.8, 58.3), color=(52, 73, 94)); sfx(tw(4, "norte"), "pop", 0.6)
ov(tw(4, "gigante"), "pin", geo=EKO, text="EKOFISK"); sfx(tw(4, "gigante"), "ding", 0.8)
# L5 lo que casi ningún país hace
sfx(tw(5) - 1.2, "riser", 0.7)
cut(tw(5), photo(P("oilsea_0"), 1.0, 1.12, blur=5), sfx="impact", gain=0.6)
ov(tw(5), "big", text="LO QUE CASI|NADIE HACE", color=YEL, y=480, size=150)
# L6 1. el petróleo es del pueblo
cut(tw(6), photo(P("family_1"), 1.12, 1.0))
ov(tw(6), "title", text="1 · EL PETRÓLEO|ES DEL PUEBLO", color=WHITE, box=GREEN, y=330); sfx(tw(6), "ding", 0.6)
ov(tw(6, "mayor"), "chip", text="GANANCIAS PARA EL ESTADO", y=1100, x=540); sfx(tw(6, "mayor"), "pop", 0.7)
# L7 2. no se lo gastan: fondo en 1990
cut(tw(7), photo(P("piggy_3"), 1.0, 1.12))
ov(tw(7), "title", text="2 · NO SE LO|GASTAN", color=WHITE, box=BLUE, y=330); sfx(tw(7), "ding", 0.6)
cut(tw(7, "1990"), photo(P("vault_1"), 1.0, 1.15), sfx="whoosh_fast")
ov(tw(7, "1990"), "counter", a=1980, b=1990, dur=0.5, y=330); sfx(tw(7, "1990"), "pop", 0.6)
ov(tw(7, "fondo"), "chip", text="FONDO DEL PETRÓLEO", y=1100, x=540); sfx(tw(7, "guardan"), "coins", 0.8)
# L8 ¿por qué? todo se encarece, las demás industrias mueren
cut(tw(8), photo(P("money_1"), 1.12, 1.0))
ov(tw(8), "big", text="¿POR QUÉ?", color=YEL, y=420, size=170); sfx(tw(8), "pop", 0.7)
cut(tw(8, "encarece"), photo(P("prices_0"), 1.0, 1.12), sfx="whoosh_fast")
ov(tw(8, "encarece"), "title", text="TODO SE|ENCARECE", color=WHITE, box=RED, y=340)
cut(tw(8, "industrias"), photo(P("fishing_2"), 1.12, 1.0), sfx="whoosh_fast")
ov(tw(8, "industrias"), "title", text="LAS DEMÁS INDUSTRIAS|SE MUEREN", color=WHITE, box=DARK, y=340, size=100)
# L9 enfermedad holandesa
cut(tw(9), photo(P("windmill_1"), 1.0, 1.12))
ov(tw(9, "enfermedad"), "title", text="ENFERMEDAD|HOLANDESA", color=YEL, y=340); sfx(tw(9, "enfermedad"), "impact", 0.5)
# L10 lo invierten afuera, miles de empresas
cut(tw(10), photo(P("city_2"), 1.0, 1.15))
ov(tw(10, "fuera"), "title", text="LO INVIERTEN|AFUERA", color=WHITE, box=GREEN, y=340); sfx(tw(10, "fuera"), "whoosh", 0.6)
cut(tw(10, "miles"), photo(P("stock_2"), 1.12, 1.0), sfx="whoosh_fast")
ov(tw(10, "miles"), "chip", text="MILES DE EMPRESAS", y=1100, x=540); sfx(tw(10, "miles"), "pop", 0.7)
# L11 1,5% de las acciones del planeta
cut(tw(11), photo(P("stock_0"), 1.0, 1.12))
ov(tw(11, "15"), "big", text="1,5%", color=YEL, y=400, size=240); sfx(tw(11, "15"), "ding", 0.8)
ov(tw(11, "acciones"), "title", text="DE TODAS LAS ACCIONES|DEL MUNDO", color=WHITE, box=DARK, y=760, size=96)
# L12 3. la regla de oro
cut(tw(12), photo(P("rule_0"), 1.0, 1.12))
ov(tw(12, "regla"), "title", text="3 · LA REGLA|DE ORO", color=WHITE, box=(230, 126, 34), y=330); sfx(tw(12, "regla"), "ding", 0.6)
cut(tw(12, "gobierno"), photo(P("oslo_2"), 1.12, 1.0), sfx="whoosh_fast")
ov(tw(12, "gana"), "chip", text="SOLO GASTA LO QUE GANA", y=1100, x=540); sfx(tw(12, "gana"), "pop", 0.7)
ov(tw(12, "3"), "counter", a=0, b=3, dur=0.4, y=380, suf="%", size=240); sfx(tw(12, "3"), "pop", 0.7)
ov(tw(12, "resto"), "stamp", text="NO SE TOCA", color=RED, y=820); sfx(tw(12, "resto"), "lock", 0.9)
# L13 más de 2 billones / 400.000 por noruego
cut(tw(13), photo(P("money_0"), 1.0, 1.12))
ov(tw(13, "billones"), "title", text="+2 BILLONES|DE DÓLARES", color=YEL, y=340); sfx(tw(13, "billones"), "coins", 0.9)
cut(tw(13, "400"), photo(P("family_0"), 1.12, 1.0), sfx="whoosh_fast")
ov(tw(13, "400"), "counter", a=0, b=400000, dur=1.0, y=380, pre="US$ ", thousands=True, size=190); sfx(tw(13, "400"), "coins", 1.0)
ov(tw(13, "noruego"), "chip", text="POR CADA NORUEGO", y=1100, x=540); sfx(tw(13, "noruego"), "ding", 0.8)
# L14 lo irónico: carros eléctricos
cut(tw(14), photo(P("oilrig_3"), 1.0, 1.12))
ov(tw(14, "ironico"), "title", text="LO MÁS|IRÓNICO", color=WHITE, box=DARK, y=340); sfx(tw(14, "ironico"), "pop", 0.7)
cut(tw(14, "carros"), photo(P("ev_3"), 1.12, 1.0), sfx="whoosh_fast")
ov(tw(14, "electricos"), "pie", frac=0.96, label="96%", y=760); sfx(tw(14, "electricos"), "ding", 0.8)
ov(tw(14, "electricos"), "title", text="CARROS ELÉCTRICOS", color=WHITE, box=GREEN, y=340)
# L15 no fue por el petróleo
cut(tw(15), photo(P("fjord_2"), 1.0, 1.12))
ov(tw(15, "encontrar"), "title", text="NO FUE POR|EL PETRÓLEO", color=WHITE, box=DARK, y=340)
ov(tw(15, "muchos"), "chip", text="MUCHOS LO ENCONTRARON", y=1100, x=540); sfx(tw(15, "muchos"), "pop", 0.6)
# L16 sino por no gastárselo
cut(tw(16), photo(P("lofoten_1"), 1.12, 1.0))
ov(tw(16, "gastarselo"), "title", text="FUE POR NO|GASTÁRSELO", color=YEL, y=340); sfx(tw(16, "gastarselo"), "impact", 0.6)
# L17 CTA
cut(tw(17), photo(P("flag_1"), 1.15, 1.0))
ov(tw(17), "big", text="¿QUÉ PAÍS|SIGUE?", color=YEL, y=290, size=125); sfx(tw(17), "pop", 0.8)
ov(tw(17, "comentarios") - 0.4, "comment", y=880, txt="Dubái, Japón..."); sfx(tw(17, "comentarios") - 0.4, "pop", 0.8)
ov(VOICE_END + 0.05, "follow", y=1090); sfx(VOICE_END + 0.05, "ding", 0.7)
