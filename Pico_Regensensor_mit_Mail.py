#Regensensor Regen-/Wassererkennung für Raspberry Pico mit Wasser Sensor YL-38 FC-37
#Bibliothek umail.py muss ebenfalls auf den Pico kopiert werden 

# Bibliotheken laden
import machine
import network
import rp2
import utime as time
import umail

# Konfiguration der GPIO-Pins
#Eingang Pin 31 am Board für Analogwert
SENSOR_PIN = machine.ADC(0)	
#Eingang für Kontakt (Empfindlichkeit über Poti einstellbar)
#GP15 entspricht PIN 20 am Board
SWITCH_PIN = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP) 
LED_PIN = machine.Pin(17, machine.Pin.OUT)

# WLAN-Verbindung herstellen
wlanSSID = 'WLAN-Name'
wlanPW = 'WLAN-Kennwort'
rp2.country('DE')

# E-Mail-Konfiguration (Sender)
smtpHost = 'smtp.web.de'   # smtp des Mailprividers eintragen
smtpPort = 587  # smtp-Port des Mailproviders eintragen
fromName = 'Name für Mailversand'
fromMail = 'Email-Anmeldeadresse'
fromPW = 'Email-Kennwort'

# E-Mail-Konfiguration (Empfänger)
toName = 'Name für Mailempfänger'
toMail = 'Email-Empfängeradresse'

# E-Mail: Betreff und Text bei Bedarf anpassen
mailSubject = 'E-Mail von Raspberry Pi Pico W'
mailText = 'Wasser in der Garage!' + "\n" + 'Diese E-Mail wurde von einem Raspberry Pi Pico W verschickt.'
mailversand = 0

# Status-LED für die WLAN-Verbindung
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# WLAN-Verbindung herstellen
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    print('WLAN-Verbindung herstellen')
    wlan.active(True)
    wlan.connect(wlanSSID, wlanPW)
    for i in range(10):
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        led_onboard.toggle()
        print('.')
        time.sleep(1)

# WLAN-Verbindung prüfen
if wlan.isconnected():
    print('WLAN-Verbindung hergestellt / WLAN-Status:', wlan.status())
    led_onboard.on()
    ipconfig = wlan.ifconfig()
    print('IPv4-Adresse:', ipconfig[0])
else:
    led_onboard.off()
    print('WLAN-Status:', wlan.status())
    raise RuntimeError('Keine WLAN-Verbindung')

# Schleife, die den Regensensor und den Schalter überwacht
while True:
    # Regensensor lesen (Wert zwischen 0 und 65535)
    sensor_value = SENSOR_PIN.read_u16()

    # Wenn der Regensensor einen nassen Wert anzeigt, die LED einschalten und eine E-Mail senden
    if sensor_value < 30000 and SWITCH_PIN.value() == 0:
        LED_PIN.on()

        # Mail senden
        if mailversand == 0:       
           # E-Mail senden
           print('E-Mail wird gesendet')
           smtp = umail.SMTP(smtpHost, smtpPort)
           smtp.login(fromMail, fromPW)
           smtp.to(toMail)
           smtp.write('From: ' + fromName + ' <' + fromMail + '>' + "\r\n")
           smtp.write('To: ' + toName + ' <' + toMail + '>' + "\r\n")
           smtp.write('Subject: ' + mailSubject + "\r\n\r\n")
           smtp.write(mailText + "\r\n")
           smtp.send()
           smtp.quit()
           print(sensor_value)
           mailversand = 1

    # Andernfalls die LED ausschalten
    else:
        LED_PIN.off()
        mailversand = 0

    # Eine kurze Pause einlegen, um den Pico nicht zu überlasten
    time.sleep_ms(100)
    
