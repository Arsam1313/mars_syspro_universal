# 🍎 DineSysPro Installationsguide

## För macOS användare

### Vilken version ska jag ladda ner?

**Apple Silicon (M1/M2/M3 chip):**
- Ladda ner: `DineSysPro-X.X.X-macOS-ARM64.dmg`
- Om din Mac köptes 2020 eller senare, har den troligen Apple Silicon

**Intel Macs:**
- Ladda ner: `DineSysPro-X.X.X-macOS-Intel.dmg`
- Äldre Macs (före 2020) har Intel-processorer

**Vet inte vilken du har?**
1. Klicka på Apple-logotypen (🍎) i övre vänstra hörnet
2. Välj **Om den här datorn**
3. Leta efter **Chip** eller **Processor**:
   - Om det står "Apple M1/M2/M3" → Använd ARM64-versionen
   - Om det står "Intel" → Använd Intel-versionen

### Problem: "Du kan inte öppna appen DineSysPro eftersom den inte stöds på den här datorn"

Detta kan hända av två anledningar:

**1. Fel version nedladdad:**
- Kontrollera att du har laddat ner rätt version (ARM64 vs Intel)
- Se guiden ovan för att ta reda på vilken chip din Mac har

**2. macOS Gatekeeper blockerar appen:**
- Detta händer eftersom applikationen inte är signerad av Apple

### Snabblösning (Rekommenderas):

Öppna **Terminal** och kör följande kommando:

```bash
xattr -cr /Applications/DineSysPro.app
```

Om du har appen i Downloads-mappen:

```bash
xattr -cr ~/Downloads/DineSysPro.app
```

Försök sedan öppna appen igen. Den ska nu fungera! ✅

---

### Alternativ Metod:

1. **Högerklicka** på `DineSysPro.app`
2. Välj **Öppna** från menyn
3. Klicka på **Öppna** i varningsrutan

Efter första gången fungerar appen normalt.

---

## För Windows användare

### Steg 1: Ladda ner

Ladda ner `DineSysPro.exe` eller `DineSysPro-Setup.exe`

### Steg 2: Installation

- **Setup.exe**: Dubbelklicka och följ installationsguiden
- **DineSysPro.exe**: Detta är en portabel version - dubbelklicka för att köra

### Windows Defender varning

Om Windows Defender visar en varning:

1. Klicka på **More info**
2. Klicka på **Run anyway**

---

## Första konfiguration

### Steg 1: Öppna Inställningar

Klicka på **⚙️** knappen (nederst till höger)

### Steg 2: Välj Skrivare

**För USB-skrivare:**
1. Välj **USB** som typ
2. Anslut skrivaren till datorn
3. Klicka på **Scan USB Printers**
4. Välj din skrivare från listan

**För Nätverksskrivare (LAN):**
1. Välj **LAN** som typ
2. Ange skrivarens IP-adress (t.ex. `192.168.1.80`)
3. Eller klicka på **Scan LAN** för att hitta skrivare automatiskt

**För Bluetooth:**
1. Välj **Bluetooth** som typ
2. Klicka på **Scan Bluetooth**
3. Välj din skrivare från listan

### Steg 3: Välj Pappersstorlek

- **58mm** - för mindre termiska skrivare
- **80mm** - för standard termiska skrivare (mest vanligt)

### Steg 4: Spara

Klicka på **Save Settings** för att spara inställningarna.

---

## Testa Skrivaren

1. Öppna Inställningar (⚙️)
2. Klicka på **Test Print**
3. Skrivaren ska skriva ut en testkvitto

---

## Funktioner

### 🖨️ Automatisk Utskrift
När en ny beställning kommer in skrivs den automatiskt ut.

### 🔊 Ljudnotiser
- **Ny beställning**: Spelar ett ljud när ny order kommer
- **Internet förlorat**: Varnar när internetanslutningen bryts
- **Lågt batteri**: Varnar när batterinivån är låg

### 🌐 Webb-integration
Appen visar beställningssystemet i fullskärmsläge.

---

## Felsökning

### Skrivaren skriver inte ut

**Kontrollera:**
- Är skrivaren påslagen?
- Är USB/nätverkskabeln ansluten?
- Är rätt skrivarnamn/IP-adress konfigurerat?
- Fungerar skrivaren när du testar från datorn direkt?

**Lösning:**
1. Öppna Inställningar
2. Klicka på **Test Print**
3. Om det inte fungerar, kontrollera anslutningen

### Appen startar inte (macOS)

```bash
# Kör i Terminal:
xattr -cr /Applications/DineSysPro.app
```

### Appen startar inte (Windows)

- Högerklicka på appen → **Kör som administratör**
- Kontrollera Windows Defender-inställningar

### Inget ljud hörs

- Kontrollera datorns volym
- Kontrollera att ljudfiler finns i `sounds/` mappen
- Starta om appen

### Internet-varning visas hela tiden

- Kontrollera din internetanslutning
- Kontrollera brandväggsinställningar
- Starta om routern

---

## System krav

### macOS
- macOS 10.14 eller senare
- Fungerar på både Intel och Apple Silicon (M1/M2/M3)

### Windows
- Windows 10 eller senare
- 64-bit system

### Skrivare
- Termisk kvittoskrivare (ESC/POS-kompatibel)
- Stödda märken: HPRT, Star, Epson, eller generisk ESC/POS

---

## Support

### Problem eller frågor?

- 🐛 [Rapportera problem på GitHub](https://github.com/Arsam1313/mars_syspro_universal/issues)
- 📧 Email: support@dinesyspro.com
- 📖 [Fullständig dokumentation](https://github.com/Arsam1313/mars_syspro_universal)

---

## Uppdateringar

Appen söker automatiskt efter nya versioner. När en uppdatering finns tillgänglig visas en notis.

För att uppdatera manuellt:
1. Ladda ner senaste versionen från [GitHub Releases](https://github.com/Arsam1313/mars_syspro_universal/releases)
2. Ersätt den gamla appen med den nya

---

## Tips

### ⌨️ Kortkommandon (macOS)
- `⌘ + Q` - Avsluta appen
- `⌘ + W` - Stäng fönster
- `⌘ + ,` - Öppna inställningar (om tillgängligt)

### 🖥️ Fullskärmsläge
Appen körs i fullskärmsläge för att passa POS-terminaler.

### ☕ Skärmsparläge
Appen förhindrar att datorn går i viloläge under drift för att säkerställa kontinuerlig service.

---

**🎉 Lycka till med DineSysPro!**

