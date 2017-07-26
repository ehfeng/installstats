from celery.schedules import crontab
from flask import render_template

from installstats.models import Source
from installstats.forms import SourceForm

from installstats import app, db, celery

@celery.task(name='tasks.get_stats')
def get_stats():
    # TODO(ehfeng) Do these in parallel
    for source in Source.query.all():
        db.session.add(source.get_stats())
    db.session.commit()


celery.conf.beat_schedule = {
    'get-stats-once-a-day': {
        'task': 'tasks.get_stats',
        'schedule': crontab(hour=0, minute=0),
    },
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/source/new')
def create_source():
    form = SourceForm()
    if form.validate_on_submit():
        source = Source(language=form.language.data, name=form.name.data)
        db.session.add(source)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_source.html', form=form)
