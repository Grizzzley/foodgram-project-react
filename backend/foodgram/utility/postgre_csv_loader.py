import csv
import logging

import psycopg2 as pg


def csv_loader():
    logger = logging.getLogger(__name__)
    file = r'./utility/ingredients.csv'
    sql_insert = """INSERT INTO recipes_ingredient(
        ingredient, measurement_unit
    )VALUES(%s, %s)"""
    try:
        conn = pg.connect(
            "host=db dbname=postgres user=postgres password=postgres"
        )
        cursor = conn.cursor()
        with open(file, 'r') as f:
            reader = csv.reader(f)
            for record in reader:
                cursor.execute(sql_insert, record)
                conn.commit()
    except (Exception, pg.Error) as e:
        logger.error(e)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            logger.info('Connection closed.')


if __name__ == '__main__':
    csv_loader()
