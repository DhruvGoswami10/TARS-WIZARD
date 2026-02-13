# API Keys Setup

TARS uses three external services. This guide walks you through getting credentials for each.

## 1. OpenAI API Key (Required)

Powers TARS's conversational AI — the sarcastic personality and responses.

### Get your key:
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** in the left sidebar
4. Click **Create new secret key**
5. Copy the key — you won't see it again

### Add to your code:
```python
openai.api_key = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx'
```

> **Cost:** OpenAI charges per token. TARS uses `gpt-3.5-turbo` with `max_tokens=50`, so each response costs fractions of a cent. A few dollars of credit will last a long time.

## 2. AWS Polly (Required)

Converts TARS's text responses into speech. Polly provides natural-sounding voices in multiple languages.

### Create an AWS account:
1. Go to [aws.amazon.com](https://aws.amazon.com/) and create an account
2. You'll need a credit card, but Polly has a generous free tier (5 million characters/month for 12 months)

### Create IAM credentials:
1. Go to the [IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Users → Create user**
3. Name it something like `tars-polly`
4. Click **Next**
5. Select **Attach policies directly**
6. Search for and attach: `AmazonPollyReadOnlyAccess`
7. Click through to create the user
8. Click on the user → **Security credentials** tab
9. Click **Create access key**
10. Select **Application running outside AWS**
11. Copy both the **Access Key ID** and **Secret Access Key**

### Add to your code:
```python
ACCESS_KEY = 'AKIAxxxxxxxxxxxxxxxx'
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

## 3. OpenWeatherMap (Optional)

Lets TARS tell you the weather with a sarcastic twist.

### Get your key:
1. Go to [openweathermap.org](https://openweathermap.org/)
2. Sign up for a free account
3. Go to **API Keys** in your profile
4. Copy your default key (or generate a new one)

### Add to your code:
```python
WEATHER_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
CITY_NAME = 'Toronto'  # Your city name
```

> **Note:** The free tier allows 1,000 API calls/day — more than enough.

## Where to Put the Keys

You need to update the keys in **two places** depending on which mode you use:

| Mode | File to edit |
|------|-------------|
| TARSmaster (desktop) | `software/TARSmaster.py` |
| Bundle (headless Pi) | `software/bundle/voice.py` |

Open the file and find the placeholder values near the top:

```python
openai.api_key = 'YOUR OPENAI API KEY HERE'     # ← Replace
ACCESS_KEY = 'YOUR AWS ACCESS KEY HERE'          # ← Replace
SECRET_KEY = 'YOUR AWS SECRET KEY HERE'          # ← Replace
WEATHER_API_KEY = 'WEATHER API KEY HERE'         # ← Replace
CITY_NAME = 'YOUR CITY NAME HERE'               # ← Replace
```

## Security Note

**Never commit your real API keys to GitHub.** The placeholder values in this repo are intentional. If you fork this project, make sure your keys stay local.

## Next Steps

- [Run TARSmaster Mode](tarsmaster-mode.md) (desktop with GUI)
- [Run Bundle Mode](bundle-mode.md) (headless Pi)
