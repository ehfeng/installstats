from datetime import date, datetime, timedelta
import enum

import requests

from installstats import bigquery_client, db


class SourceLanguage(enum.Enum):
    python = "python"
    ruby = "ruby"
    node = "node"
    php = "php"
    cocoa = "cocoa"
    csharp = "csharp"


class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    count = db.Column(db.Integer)
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))

    source = db.relationship('Source', backref=db.backref('stats', lazy='dynamic'))

    def __init__(self, date, count, source):
        self.date = date
        self.count = count
        self.source = source


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.Enum(SourceLanguage))
    name = db.Column(db.Text)

    def __init__(self, language, name):
        self.language = language
        self.name = name

    def get_stats(self):
        if self.language == SourceLanguage.node:
            return self.get_npm_stats()
        elif self.language == SourceLanguage.python:
            return self.get_pip_stats()
        elif self.language == SourceLanguage.ruby:
            return self.get_gem_stats()
        elif self.language == SourceLanguage.php:
            return self.get_composer_stats()
        elif self.language == SourceLanguage.csharp:
            return self.get_nuget_stats()

    def get_npm_stats(self):
        data = requests.get("https://api.npmjs.org/downloads/point/last-day/{}".format(self.name)).json()
        return Stat(
            date=datetime.strptime(data['start'], '%Y-%m-%d'),
            count=data['downloads'],
            source=self)

    def get_pip_stats(self):
        yesterday = date.today() - timedelta(days=1)
        job = bigquery_client.run_sync_query("""
            SELECT file.project, count(1) as count FROM `the-psf.pypi.downloads{date}`
            WHERE file.project='{name}'
            GROUP BY file.project
            """.format(date=yesterday.strftime('%Y%m%d'),
                name=self.name))
        job.use_legacy_sql = False
        job.run()
        return Stat(
            date=yesterday,
            count=job.rows[0][1],
            source=self
            )

    def get_gem_stats(self):
        yesterday = date.today() - timedelta(days=1)
        gem_data = requests.get('/api/v1/gems/{}.json'.format(self.name),
            headers={'Authorization': os.environ.get('RUBYGEMS_API_KEY')}).json()
        data = requests.get('https://rubygems.org/api/v1/downloads/{name}-{version}.json'.format(
            name=self.name, version=gem_data['version']),
            headers={'Authorization': os.environ.get('RUBYGEMS_API_KEY')}).json()
        last_stat = Stat.query.filter(source=source).order_by(Stat.date.desc()).first()
        yesterday = datetime.now() - timedelta(days=1)
        assert yesterday - last_stat.date == timedelta(days=1)
        return Stat(
            date=yesterday,
            count=data['total_downloads'] - last_stat.count,
            source=self)

    def get_composer_stats(self):
        # self.name should be sentry/sentry
        yesterday = date.today() - timedelta(days=1)
        data = requests.get('https://packagist.org/packages/%s.json' % self.name).json() # sentry/sentry
        last_stat = Stat.query.filter(source=source).order_by(Stat.date.desc()).first()
        assert yesterday - last_stat.date == timedelta(days=1)
        return Stat(
            date=yesterday,
            count=data['downloads'] - last_stat.count,
            source=self)

    def get_cocoapod_stats(self):
        yesterday = date.today() - timedelta(days=1)
        data = requests.get('http://metrics.cocoapods.org/api/v1/pods/%s' % self.name).json()
        data['stats']['download_total']
        data['stats']['app_total']
        last_stat = Stat.query.filter(source=source).order_by(Stat.date.desc()).first()
        assert yesterday - last_stat.date == timedelta(days=1)
        return Stat(
            date=yesterday,
            count=data['stats']['download_total'] - last_stat.count,
            source=self)

    def get_nuget_stats(self):
        raise NotImplemented
