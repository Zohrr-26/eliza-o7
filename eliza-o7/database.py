"""
Services pour la gestion de la base de données SQL Server (Azure)
"""
import pyodbc
import logging
import os
from models import New_ID

DB_CONN_STR = os.getenv("DB_CONN_STR") 

def init_database():
    """Initialise la table de l'historique si elle n'existe pas"""
    conn = None
    try:
        conn = pyodbc.connect(DB_CONN_STR)
        cursor = conn.cursor()
        
        # IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='predictions_history' AND xtype='U')
        create_table_sql = f"""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='predictions_history')
        CREATE TABLE predictions_history (
            id INT IDENTITY(1,1) PRIMARY KEY,
            prediction_date DATETIME2 DEFAULT GETDATE(),
            predicted_price FLOAT,
            {', '.join([f'{field} NVARCHAR(255)' for field in New_ID.fields])}
        )"""
        
        cursor.execute(create_table_sql)
        conn.commit()
        logging.info(f"Base de données initialisée (azure_sql)")
        
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de la base : {e}")
        raise

    finally: 
        if conn is not None:
            conn.close()

def save_prediction(prediction_data: New_ID, predicted_price: float):
    """Sauvegarde une prédiction dans l'historique"""
    conn = None
    try:
        conn = pyodbc.connect(DB_CONN_STR)
        cursor = conn.cursor()
        
        field_values = [str(value) for value in prediction_data.to_list()]        

        insert_sql = f"""
        INSERT INTO predictions_history (predicted_price, {', '.join(New_ID.fields)})
        VALUES (?, {', '.join(['?'] * len(New_ID.fields))})
        """
        
        cursor.execute(insert_sql, [predicted_price] + field_values)
        conn.commit()
        logging.info(f"Prédiction sauvegardée : {predicted_price}")
        
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde : {e}")
        raise

    finally:
        if conn is not None:
            conn.close()

def get_predictions_history(limit: int = 13):
    """Récupère l'historique des prédictions"""
    
    conn = None
    try:
        conn = pyodbc.connect(DB_CONN_STR)
        cursor = conn.cursor()

        select_sql = f"""
        SELECT TOP (?) predicted_price, {', '.join(New_ID.fields)}
        FROM predictions_history 
        ORDER BY prediction_date DESC
        """
        
        cursor.execute(select_sql, (limit,))
        rows = cursor.fetchall()
        
        # Convertir en liste de dictionnaires
        history = []
        for row in rows:
            history.append({'predicted_price': row[0],
                            **{field: row[i+1] for i, field in enumerate(New_ID.fields)}
                            })
        
        return history
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de l'historique : {e}")
        return []
    
    finally:
        if conn is not None:
            conn.close()
