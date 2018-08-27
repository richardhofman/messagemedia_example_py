# MessageMedia Python API Client

This repository contains a simple (and rather haphazard) Python script, which uses `v1` of the [MessageMedia](https://www.messagemedia.com) REST API to send an SMS message to a specified phone number. It was developed as an entry into a small prize draw, for a chance to win some awesome BOSE headphones. Regardless of the outcome of the draw, this has been a fun 45 minute project - maybe it'll even be useful to someone!

## Usage

To run the script, you first must have the dependencies installed. You can do this easily by running `pip install -r requirements.txt` inside this repository.

The script looks for two environment variables to use for API credentials. These *must* be special HMAC API keys, which can be generated at the bottom of the [API Settings](https://hub.messagemedia.com/api-settings) page:

* `MESSAGEMEDIA_APIKEY`
* `MESSAGEMEDIA_APISECRET`

In addition, it accepts two arguments on the command line:

`mm_sender.py <phone_number> <message_content>`

where `<phone_number>` can be either an E.164 international-format number (e.g. "+61432123456"), or an Australian local-format number (e.g. 0432 123 456). Whitespace is ignored in either case. `<message_content>` shouldn't need any explanation.
