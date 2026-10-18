from .run_command_grid import (
    run_command_grid,
    run_command_grid_eq,
    run_command_min_max,
    run_command_draw_extra,
    run_command_transient,
    run_command_exoplanets,
    run_command_image_cutout,
    run_command_asteroids,
)
from .run_command_stars import run_command_stars

def dispatch_job(command, observation_id, params):
    # when 'queue' is specified in the Job object, then it will be picked up by Celery.
    # otherwise it will be picked up by the old pip instaled astrobase_services

    # test the 'astro' queue, which will be picked up by celery
    if command == "ping":
        job = Job(command='ping', job_service='celery', queue='celery', status="new")
        job.save()

    if command == "grid":
        run_command_grid(observation_id)

    if command == "grid_eq":
        run_command_grid_eq(observation_id)

    if command == "stars":
        run_command_stars(observation_id)

    if command == "min_max":
        run_command_min_max(observation_id)

    if command == "draw_extra":
        run_command_draw_extra(observation_id)

    if command == "transient":
        run_command_transient(observation_id)

    if command == "exoplanets":
        run_command_exoplanets(observation_id)

    if command == "image_cutout":
        run_command_image_cutout(params)

    if command == "asteroids":
        run_command_asteroids(observation_id)

    return "dispatched"