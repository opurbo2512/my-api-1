#importing librarys
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import sqlite3

#function for distance calculation
def distance(x1,x2,p):
    p = np.array(p)
    p = p/np.sum(p)
    score = 0
    for i in range(len(x1)):
        score += (1-abs(x1[i]-x2[i])) * p[i]
    return score


#function for getting material id
def calculate_materials(values,priority):
    df = pd.read_csv("Data/working_data.csv")
    X = df.drop("material_id",axis=1)
    scores = []
    for i in range(len(X)):
        t = X.iloc[i].to_numpy()
        score = distance(t,values,priority)
        scores.append(score)
    max_3_index = np.argsort(scores)[-3:][::-1]
    return (max_3_index+1).tolist()

#making app
app = FastAPI()

#input basemodel
class UserInput(BaseModel):
    values : list[float]
    priority : list[float]

#main function of api
@app.post("/recommend")
def recommend(data : UserInput):
    values = data.values
    priority = data.priority

    material_ids = calculate_materials(values,priority)
    conn = sqlite3.connect("mat_database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    placeholders = ",".join("?" * len(material_ids))

    query = f"""
        SELECT *
        FROM mat_table
        WHERE material_id IN ({placeholders})
    """
    cursor.execute(query, material_ids)

    rows = cursor.fetchall()

    conn.close()

    return {
        "materials": [dict(row) for row in rows]
    }

        



