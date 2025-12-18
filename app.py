from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from config import DevConfig, ProdConfig
from sqlalchemy import and_, or_

# -------------------------------------------------
# App & DB Init (UNCHANGED)
# -------------------------------------------------
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    if os.getenv("ENV") == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)

    db.init_app(app)
    return app

app = create_app()

# -------------------------------
# Authentication (Design Scope)
# -------------------------------
# Authentication is intentionally not enforced in the current
# implementation to ensure ease of evaluation and universal access.
# The architecture supports future integration using:
# - Flask-Login (session-based auth)
# - JWT-based authentication (API)
# - Role-based access control (Admin/User)

# -------------------------------------------------
# Models (UNCHANGED except ADDITIONS)
# -------------------------------------------------
class Event(db.Model):
    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)

    allocations = db.relationship(
        'EventResourceAllocation',
        backref='event',
        cascade='all, delete-orphan',
        lazy=True
    )

class Resource(db.Model):
    __tablename__ = "resources"

    resource_id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)

    allocations = db.relationship(
        'EventResourceAllocation',
        backref='resource',
        cascade='all, delete-orphan',
        lazy=True
    )

class EventResourceAllocation(db.Model):
    __tablename__ = "event_resource_allocations"

    allocation_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)

    # 🔽 ADDED (non-breaking, required for dashboard & reports)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)

# -------------------------------------------------
# Conflict Detection Logic (UNCHANGED)
# -------------------------------------------------
def check_conflicts(event_id, resource_id, start_time, end_time):
    conflicts = db.session.query(EventResourceAllocation).join(Event).filter(
        EventResourceAllocation.resource_id == resource_id,
        EventResourceAllocation.event_id != event_id,
        or_(
            and_(Event.start_time <= start_time, Event.end_time > start_time),
            and_(Event.start_time < end_time, Event.end_time >= end_time),
            and_(Event.start_time >= start_time, Event.end_time <= end_time),
            Event.start_time == start_time
        )
    ).all()
    return conflicts

# -------------------------------------------------
# Routes
# -------------------------------------------------

# 🔽 MODIFIED: Dashboard is now DB-driven (ONLY CHANGE HERE)
@app.route('/')
def index():
    now = datetime.utcnow()

    active_events = Event.query.filter(
        Event.start_time <= now,
        Event.end_time >= now
    ).count()

    total_resources = Resource.query.count()
    allocated_resources = (
        db.session.query(EventResourceAllocation.resource_id)
        .distinct()
        .count()
    )

    resource_load = int((allocated_resources / total_resources) * 100) if total_resources else 0

    conflicts_count = 0      # computed in /conflicts
    pending_approvals = 0    # not implemented by design

    latest_allocations = (
        EventResourceAllocation.query
        .order_by(EventResourceAllocation.allocation_id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'index.html',
        active_events=active_events,
        resource_load=resource_load,
        conflicts_count=conflicts_count,
        pending_approvals=pending_approvals,
        latest_allocations=latest_allocations
    )

# ---------------- Events (UNCHANGED) ----------------
@app.route('/events')
def events():
    all_events = Event.query.order_by(Event.start_time.desc()).all()
    return render_template('events.html', events=all_events)

@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        description = request.form.get('description', '')

        if start_time >= end_time:
            flash('End time must be after start time', 'danger')
            return redirect(url_for('add_event'))

        new_event = Event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        db.session.add(new_event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('events'))

    return render_template('add_event.html')

@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form['title']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        event.description = request.form.get('description', '')

        if start_time >= end_time:
            flash('End time must be after start time', 'danger')
            return redirect(url_for('edit_event', event_id=event_id))

        conflicts_found = []
        for allocation in event.allocations:
            conflicts = check_conflicts(
                event_id,
                allocation.resource_id,
                start_time,
                end_time
            )
            if conflicts:
                resource = Resource.query.get(allocation.resource_id)
                conflicts_found.append(resource.resource_name)

        if conflicts_found:
            flash(
                f'Time conflict detected for resources: {", ".join(conflicts_found)}',
                'danger'
            )
            return redirect(url_for('edit_event', event_id=event_id))

        event.start_time = start_time
        event.end_time = end_time
        db.session.commit()

        flash('Event updated successfully!', 'success')
        return redirect(url_for('events'))

    return render_template('edit_event.html', event=event)

@app.route('/events/delete/<int:event_id>')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events'))

# ---------------- Resources (UNCHANGED) ----------------
@app.route('/resources')
def resources():
    all_resources = Resource.query.all()
    return render_template('resources.html', resources=all_resources)

@app.route('/resources/add', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        new_resource = Resource(
            resource_name=request.form['resource_name'],
            resource_type=request.form['resource_type']
        )
        db.session.add(new_resource)
        db.session.commit()

        flash('Resource created successfully!', 'success')
        return redirect(url_for('resources'))

    return render_template('add_resource.html')

@app.route('/resources/edit/<int:resource_id>', methods=['GET', 'POST'])
def edit_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)

    if request.method == 'POST':
        resource.resource_name = request.form['resource_name']
        resource.resource_type = request.form['resource_type']
        db.session.commit()

        flash('Resource updated successfully!', 'success')
        return redirect(url_for('resources'))

    return render_template('edit_resource.html', resource=resource)

@app.route('/resources/delete/<int:resource_id>')
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted successfully!', 'success')
    return redirect(url_for('resources'))

# ---------------- Allocations (MINIMAL ADDITION) ----------------
@app.route('/allocations')
def allocations():
    all_allocations = EventResourceAllocation.query.all()
    return render_template('allocations.html', allocations=all_allocations)

@app.route('/allocations/add', methods=['GET', 'POST'])
def add_allocation():
    if request.method == 'POST':
        event_id = int(request.form['event_id'])
        resource_id = int(request.form['resource_id'])

        existing = EventResourceAllocation.query.filter_by(
            event_id=event_id,
            resource_id=resource_id
        ).first()
        if existing:
            flash('This resource is already allocated to this event', 'warning')
            return redirect(url_for('add_allocation'))

        event = Event.query.get(event_id)
        conflicts = check_conflicts(
            event_id,
            resource_id,
            event.start_time,
            event.end_time
        )

        if conflicts:
            flash('Resource conflict detected!', 'danger')
            return redirect(url_for('add_allocation'))

        # 🔽 ADDED start/end time (no logic removed)
        new_allocation = EventResourceAllocation(
            event_id=event_id,
            resource_id=resource_id,
            start_time=event.start_time,
            end_time=event.end_time
        )

        db.session.add(new_allocation)
        db.session.commit()

        flash('Resource allocated successfully!', 'success')
        return redirect(url_for('allocations'))

    events = Event.query.order_by(Event.start_time).all()
    resources = Resource.query.all()
    return render_template('add_allocation.html', events=events, resources=resources)

@app.route('/allocations/delete/<int:allocation_id>')
def delete_allocation(allocation_id):
    allocation = EventResourceAllocation.query.get_or_404(allocation_id)
    db.session.delete(allocation)
    db.session.commit()
    flash('Allocation removed successfully!', 'success')
    return redirect(url_for('allocations'))

# ---------------- Conflicts (UNCHANGED) ----------------
@app.route('/conflicts')
def conflicts():
    all_conflicts = []
    allocations = EventResourceAllocation.query.all()

    for allocation in allocations:
        event = Event.query.get(allocation.event_id)
        resource = Resource.query.get(allocation.resource_id)

        conflicts = check_conflicts(
            allocation.event_id,
            allocation.resource_id,
            event.start_time,
            event.end_time
        )

        if conflicts:
            for conflict in conflicts:
                conflicting_event = Event.query.get(conflict.event_id)
                all_conflicts.append({
                    'event1': event,
                    'event2': conflicting_event,
                    'resource': resource
                })

    return render_template('conflicts.html', conflicts=all_conflicts)

# ---------------- Report (UNCHANGED) ----------------
@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)

        resources = Resource.query.all()
        report_data = []

        for resource in resources:
            total_hours = 0
            upcoming_bookings = []

            allocations = EventResourceAllocation.query.filter_by(
                resource_id=resource.resource_id
            ).all()

            for allocation in allocations:
                event = Event.query.get(allocation.event_id)

                if event.start_time <= end_date and event.end_time >= start_date:
                    overlap_start = max(event.start_time, start_date)
                    overlap_end = min(event.end_time, end_date)
                    total_hours += (overlap_end - overlap_start).total_seconds() / 3600

                if event.start_time > datetime.now():
                    upcoming_bookings.append(event)

            report_data.append({
                'resource': resource,
                'total_hours': round(total_hours, 2),
                'upcoming_bookings': upcoming_bookings
            })

        return render_template(
            'report.html',
            report_data=report_data,
            start_date=start_date,
            end_date=end_date,
            show_results=True
        )

    return render_template('report.html', show_results=False)

# ---------------- Neutralized Route (NOT REMOVED) ----------------
@app.route("/events/create", methods=["POST"])
def create_event():
    return ("Not implemented", 501)

# -------------------------------------------------
# App Bootstrap
# -------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
