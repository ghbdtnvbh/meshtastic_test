import time
from logger import logging
from pubsub import pub
import meshtastic.serial_interface
from meshtastic.util import findPorts
from database import add_user, add_message, add_position, user_exists, add_telemetry

PORT_USB = findPorts()
logging.info(f"Connecting to {PORT_USB}")
interface = meshtastic.serial_interface.SerialInterface()


def onReceiveText(packet, interface):
    user_id = packet['fromId']
    text = packet['decoded']['text']
    add_message(user_id, text)
    
    if 'PING' in text.upper():
        interface.sendText("PONG")


def onReceiveUser(packet, interface):
    path = packet['decoded']['user']
    user_id = path['id']
    longName = path['longName']
    shortName = path['shortName']
    macaddr = path['macaddr']
    hwModel = path['hwModel']
    # При обнаружении ноды, проверяется есть ли записть в БД
    if not user_exists(user_id): 
        # Если такой записить нет, добавляется в БД и отправляем приветствие к канал.
        add_user(user_id, longName, shortName, macaddr, hwModel)
        interface.sendText(f'Привет {shortName}!')


def onReceivePosition(packet, interface):
    try:
        lat = round(packet['decoded']['position']['latitude'],6)
        lon = round(packet['decoded']['position']['longitude'],6)
        lat_lon = f"{lat},{lon}"
        user_id = packet['fromId']
        add_position(user_id, lat_lon) # Записывем координаты в БД
    except KeyError: # когда кто-то запрашивет наши координаты парсинг ломается по этому отлавливаем этот момент
        logging.warning("Кто-то запросил у нас геопозицию")


def onReceiveTelemetry(packet, interface):
    fromId_dec = packet['from']
    if interface.myInfo.my_node_num != fromId_dec:   
        path = packet['decoded']['telemetry']['deviceMetrics']
        batteryLevel = path['batteryLevel']
        voltage = path['voltage']
        airUtilTx = path['airUtilTx']
        rxSnr = packet['rxSnr']
        hopLimit = packet['hopLimit']
        rxRssi = packet['rxRssi']
        fromId_hex = packet['fromId']

        add_telemetry(fromId_hex, batteryLevel, voltage, airUtilTx, rxSnr, hopLimit, rxRssi)


def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    # interface.sendText("hello mesh")
    pass

def main():
    while True:
        try:
            pub.subscribe(onReceiveText, "meshtastic.receive.text")
            pub.subscribe(onReceiveUser, "meshtastic.receive.user")
            pub.subscribe(onReceivePosition, "meshtastic.receive.position")
            pub.subscribe(onConnection, "meshtastic.connection.established")
            pub.subscribe(onReceiveTelemetry, "meshtastic.receive.telemetry")
        except Exception as e:
            logging.exception(e)
        time.sleep(1)

if __name__ == '__main__':
    main()