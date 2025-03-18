#include <WiFi.h>

/**
 * Import macros for "SSID" & "PW".
 */
#include "ssid.h"

#define HOSTNAME "mailbox-esp32" ///< Hostname for self.
#define uS_TO_S_FACTOR 1000000ULL ///< Conversion factor for micro seconds to seconds.
#define TIME_TO_SLEEP  1 ///< Number of seconds ESP32 will go to sleep.

/** Statics. */
bool serialFlag = true; ///< Flag for printing debug to serial monitor.
IPAddress gigabyteServer(192, 168, 0, 21); ///< IP Address of home server.
const int gigabytePort = 8090; ///< Port number of home server.
const int lightTimeout = 60;
const int leftOpenTimeout = 120;
enum Message {
  OPEN,
  LEFT_OPENED
};
const char openedMsg[] = "mailbox opened";
const char leftOpenMsg[] = "mailbox left opened";

/** Pinouts. */
int ledPin = 32; ///< LED on/off pin.
int flagPin = 16; ///< Vin for optical flag.
int optoFlagEnablePin = 25; ///< Optical flag emitter power pin.

/**
 * @brief Pin modes must be set after WiFi call.
 */
void setPinModes()
{
  // Set pin mode.
  pinMode(ledPin, OUTPUT);
  pinMode(flagPin, INPUT);
  pinMode(optoFlagEnablePin, OUTPUT);
}

/**
 * @brief Setup microcontroller.
 */
void setup()
{
  setPinModes();

  // Debug.
  if(serialFlag)
  {
    Serial.begin(115200);
    return;
  }

  // Always awake code.
  return;

  /// @todo Sleep code.
  handleFlagStatus();
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  esp_deep_sleep_start();
}

/**
 * @brief Connect to WiFi & send message to gigabyte.
 */
void sendWifiMessage(Message msg)
{
  // Init & make a connection.
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(HOSTNAME);
  WiFi.begin(SSID, PW);

  if(serialFlag)
  {  
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
      Serial.print('.');
      delay(1000);
    }

    Serial.print("\nESP32 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("ESP32 HostName: ");
    Serial.println(WiFi.getHostname());
    Serial.print("RSSI: ");
    Serial.println(WiFi.RSSI());
  }

  WiFiClient client;
  if(client.connect(gigabyteServer, gigabytePort))
  {
    if(msg == OPEN) { client.print("mailbox opened"); }
    else if(msg == LEFT_OPENED) { client.print("mailbox left opened"); }
    // Need to wait; send must be async.
    delay(5000);
  }

  // Disconnect by disabling WiFi mode.
  WiFi.mode(WIFI_OFF);

  // Reset pin modes afterwards.
  setPinModes();
}

/**
 * @brief Main loop code for always awake version.
 */
void loop()
{
  // Enable optical flag first.
  digitalWrite(optoFlagEnablePin, HIGH);
  while(true)
  {
    delay(200);

    // Door is opened.
    if(digitalRead(flagPin) == HIGH)
    {
      // Turn on light.
      digitalWrite(ledPin, HIGH);

      // Wait until door is closed again or timeout.
      int timeout = 0;
      while(digitalRead(flagPin) == HIGH && timeout++ < lightTimeout) { delay(1000); }

      // Turn off light.
      digitalWrite(ledPin, LOW);

      sendWifiMessage(OPEN);

      // See if the door was left opened.
      while(digitalRead(flagPin) == HIGH && timeout++ < leftOpenTimeout) { delay(1000); }

      if(timeout >= leftOpenTimeout)
      {
        // Send status the door was left opened.
        sendWifiMessage(LEFT_OPENED);

        // Reenable optical flag.
        digitalWrite(optoFlagEnablePin, HIGH);

        // Wait here until closed again.
        while(digitalRead(flagPin) == HIGH) { delay(1000); }
      }

      // Reenable optical flag.
      digitalWrite(optoFlagEnablePin, HIGH);
    }
  }
}

/**
 * @brief Handle the I/O operation of flag status.
 */
void handleFlagStatus()
{
  // Door is closed; leave.
  if(digitalRead(flagPin) == LOW) { return; }

  // Door is open; turn on light.
  digitalWrite(ledPin, HIGH);

  // Wait until door is closed again.
  while(digitalRead(flagPin) == HIGH) { delay(1000); }

  // Turn off light.
  digitalWrite(ledPin, LOW);

  // Notify server.
  sendWifiMessage(OPEN);
}

/**
 * @brief Main awake loop.
 */
void loop1()
{
  bool sentDone = false;
  while(true)
  {
    digitalWrite(optoFlagEnablePin, HIGH);
    delay(100);
    int val = digitalRead(flagPin);
    if(val == HIGH)
    {
      digitalWrite(ledPin, HIGH);
      if(!sentDone)
      {
        Serial.println("HIGH reached");
        sentDone = true;
        sendWifiMessage(OPEN);
      }
    }
    else
    {
      Serial.println("LOW");
      digitalWrite(ledPin, LOW);
      sentDone = false;
    }
  }
}