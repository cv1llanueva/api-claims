from fastapi import FastAPI, HTTPException, status
from typing import List
from fastapi import Query
import mysql.connector
import schemas
import random
import uuid
import datetime

app = FastAPI()

host_name = "52.2.83.96"  # Agrega el nombre del host de la base de datos
port_number = "8005"  # Agrega el número de puerto de la base de datos
user_name = "root"
password_db = "utec"
database_name = "bd_api_claims"  # Modifica el nombre de la base de datos


# Conexión a la base de datos
def connect_to_db():
    return mysql.connector.connect(
        host=host_name,
        port=port_number,
        user=user_name,
        password=password_db,
        database=database_name
    )

# Obtener todos los siniestros
@app.get("/api/v1/claims", response_model=List[schemas.ClaimOutput])
def get_claims():
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()

        cursor.execute("""SELECT claimNumber, policyNumber, accidentDate, description, lossAmount, isFiledByCustomer, claimDate
                          FROM Claim""")
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No claims found")

        claims = [schemas.ClaimOutput(
            claimNumber=claim[0],
            policy=schemas.Policy(
                policyNumber=claim[1],
                policyType="",
                startDate=None,
                endDate=None,
                premiumAmount=0.0
            ),
            accidentDate=claim[2],
            description=claim[3],
            lossAmount=claim[4],
            isFiledByCustomer=claim[5],
            claimDate=claim[6].strftime("%Y-%m-%dT%H:%M:%S")
        ) for claim in result]

        return claims

    except mysql.connector.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if 'mydb' in locals():
            mydb.close()

# Agregar un nuevo siniestro
@app.post("/api/v1/claim", response_model=schemas.ClaimOutput, status_code=status.HTTP_201_CREATED)
def add_claim(item: schemas.ClaimInput):
    try:
        mydb = connect_to_db()
        cursor = mydb.cursor()

        claim_number = str(uuid4())[:8]
        claim_date = datetime.now()

        sql_claim = """INSERT INTO Claim (claimNumber, policyNumber, accidentDate, description, lossAmount, isFiledByCustomer, claimDate) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val_claim = (claim_number, item.policy.policyNumber, item.accidentDate, item.description, item.lossAmount, item.isFiledByCustomer, claim_date)
        
        cursor.execute(sql_claim, val_claim)
        mydb.commit()

        claim_output = schemas.ClaimOutput(
            claimNumber=claim_number,
            policy=item.policy,
            accidentDate=item.accidentDate,
            description=item.description,
            lossAmount=item.lossAmount,
            isFiledByCustomer=item.isFiledByCustomer,
            claimDate=claim_date.strftime("%Y-%m-%dT%H:%M:%S")
        )

        return claim_output

    except mysql.connector.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if 'mydb' in locals():
            mydb.close()

# Eliminar un siniestro por su número de reclamo
@app.delete("/api/v1/claim", status_code=status.HTTP_204_NO_CONTENT)
def delete_claim(claimNumber: str):
    mydb = connect_to_db()
    cursor = mydb.cursor()
    sql = "DELETE FROM Claim WHERE claimNumber = %s"
    val = (claimNumber,)
    cursor.execute(sql, val)
    mydb.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    mydb.close()
    return {"message": "Claim deleted successfully"}