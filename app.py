from flask import Flask, render_template, request, redirect, url_for, flash
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_proxies():
    proxies = []
    if not os.path.exists("proxies.txt"):
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&limit=5000"
        proxies = requests.get(url).text.split("\n")
        with open("proxies.txt", "w") as f:
            f.write("\n".join(proxies))
    else:
        with open("proxies.txt", "r") as f:
            proxies = f.read().split("\n")
    return proxies

def google_search(query, user_agent, proxy):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": user_agent}
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    return [result["href"] for result in soup.select(".yuRUbf a")]

def search_dork(dork, proxies, user_agents):
    user_agent = random.choice(user_agents)
    proxy = random.choice(proxies)
    try:
        results = google_search(dork, user_agent, proxy)
        return results
    except Exception as e:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dorks = request.form['dorks'].strip().splitlines()
        user_agents = get_user_agents()
        proxies = get_proxies()

        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(search_dork, dork, proxies, user_agents): dork for dork in dorks}
            for future in as_completed(futures):
                result = future.result()
                dork = futures[future]
                results[dork] = result

        return render_template('results.html', results=results)

    return render_template('index.html')

def get_user_agents():
    with open("useragents.txt", "r") as f:
        return f.read().split("\n")

if __name__ == '__main__':
    app.run(debug=True)
