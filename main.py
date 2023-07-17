# coding:utf-8

import codecs
import os
import shutil
from datetime import datetime

import requests
from pyquery import PyQuery as pq


def git_add_commit_push(date, filename):
    cmd_git_add = 'git add {filename}'.format(filename=filename)
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin master'

    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)


def create_markdown(date, filename):
    with open(filename, 'w') as f:
        f.write("## " + date + "\n")


def scrape(language, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=headers)
    assert r.status_code == 200

    d = pq(r.content)
    items = d('div.Box article.Box-row')

    # codecs to solve the problem utf-8 codec like chinese
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n#### {language}\n'.format(language=language))

        for item in items:
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url
            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))


def move_files_to_current_month_folder():
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    current_month_folder = f"{current_year}/{current_month}"

    # Check if today is the last day of the month
    if (current_month in [1, 3, 5, 7, 8, 10, 12] and current_day == 31) or \
            (current_month in [4, 6, 9, 11] and current_day == 30) or \
            (current_month == 2 and current_day == 28):
        if not os.path.exists(current_month_folder):
            os.makedirs(current_month_folder)

        for file in os.listdir():
            if file.endswith(".md") and file.startswith(f"{current_year}-{str(current_month).zfill(2)}"):
                shutil.move(file, current_month_folder)
    else:
        print("Today is not the last day of the month. Files will not be moved.")


def job():
    str_date = datetime.now().strftime('%Y-%m-%d')
    filename = '{date}.md'.format(date=str_date)

    # create markdown file
    create_markdown(str_date, filename)

    # write markdown
    scrape('python', filename)
    scrape('java', filename)
    scrape('go', filename)

    # archive
    move_files_to_current_month_folder()


if __name__ == '__main__':
    job()
