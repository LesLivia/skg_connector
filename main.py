from neo4j.exceptions import AuthError

import skg_mgrs.connector_mgr as conn
from skg_logger.logger import Logger
from skg_mgrs.skg_reader import Skg_Reader, SCHEMA
from skg_mgrs.skg_writer import Skg_Writer
from skg_model.schema import Timestamp
from skg_model.semantics import EntityForest

LOGGER = Logger('main')

LOGGER.info('Starting...')

try:
    driver = conn.get_driver()
    reader = Skg_Reader(driver)

    activities = reader.get_activities()
    print(','.join([a.act for a in activities]))

    if 'date' not in SCHEMA['event_properties']:
        start_t = 0
        end_t = 300000
    else:
        start_t = Timestamp(2023, 11, 4, 13, 0, 0)
        end_t = Timestamp(2023, 11, 5, 14, 30, 0)

    events = reader.get_events_by_date(start_t, end_t)
    for e in events:
        print(e.activity)

    resource = reader.get_resources(limit=1, random=True)[0]
    print(resource.entity_id, resource.extra_attr)

    entity_tree = reader.get_entity_tree(resource.entity_id, EntityForest([]))

    events = reader.get_events_by_entity_tree_and_timestamp(entity_tree.trees[0], start_t, end_t, pov='resource')
    for e in events:
        print(e.activity, e.timestamp)

    entity = reader.get_items(limit=1, random=True)[0]
    print(entity.entity_id, entity.extra_attr)

    entity_tree = reader.get_entity_tree(entity.entity_id, EntityForest([]), reverse=True)

    events = reader.get_events_by_entity_tree_and_timestamp(entity_tree.trees[0], start_t, end_t, pov='item')
    for e in events:
        print(e.activity, e.timestamp)

    # writer = Skg_Writer(driver)
    # automaton = writer.write_automaton()
    # sensors = reader.get_entities_by_labels(['Sensor'])
    # entities = reader.get_related_entities('Sensor', 'Station', filter1='S4', limit=1, random=True)
    # for tup in entities:
    #    print(tup[0].entity_id, tup[1].entity_id)
    # writer.create_semantic_link(automaton, name='LABELED_BY', edge=automaton.edges[0],
    #                            ent=sensors[0], entity_labels=['Sensor'])
    # writer.cleanup('')

    conn.close_connection(driver)
    LOGGER.info('Testing complete.')
except AuthError:
    LOGGER.error('Connection to DB could not be established.')
