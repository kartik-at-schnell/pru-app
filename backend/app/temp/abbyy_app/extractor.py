from datetime import datetime
from typing import Optional, Dict, Any, List
from app.temp.abbyy_app.abbyy_database import DriverLicense, VehicleRegistration
from sqlalchemy.orm import Session

def parse_datetime(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        date_str = str(date_str).strip()
        formats = ["%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y", "%Y-%m-%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.split()[0], "%m/%d/%Y")
            except:
                continue
        return None
    except:
        return None

def get_field_value(fields: List[Dict], field_name: str) -> Optional[str]:
    for field in fields:
        if field.get("Name") == field_name:
            value = field.get("Value", "").strip()
            return value if value else None
    return None

def extract_driver_license_from_abbyy(batch_id: int, document_id: int, abbyy_json: Dict[str, Any]) -> Optional[DriverLicense]:
    try:
        documents = abbyy_json.get("Documents", [])
        
        dl_doc = None
        for doc in documents:
            doc_name = doc.get("Name", "").strip()
            if "DriverLicense_LeadSheet" in doc_name or doc_name == "DriverLicense_LeadSheet":
                dl_doc = doc
                break
        
        if not dl_doc:
            return None
        
        sections = dl_doc.get("Sections", [])
        if not sections:
            return None
        
        fields = sections[0].get("Fields", [])
        
        tn_dl_val = get_field_value(fields, "TN_DL")
        fn_dl_val = get_field_value(fields, "FN_DL")
        
        if not tn_dl_val or not fn_dl_val:
            return None
        
        dl = DriverLicense(
            batch_id=str(batch_id),
            document_id=str(document_id),
            tn_dl=tn_dl_val,
            fn_dl=fn_dl_val,
            agency=get_field_value(fields, "Agency"),
            transcribed_last_name=get_field_value(fields, "TLN"),
            transcribed_first_name=get_field_value(fields, "TFN"),
            first_last_name=get_field_value(fields, "FLN"),
            first_first_name=get_field_value(fields, "FFN"),
            date_issued=parse_datetime(get_field_value(fields, "Date_Issued") or ""),
            expiration_date=parse_datetime(get_field_value(fields, "Expiration_Date") or ""),
            contact=get_field_value(fields, "Contact"),
            tracking_number=get_field_value(fields, "TrackingNo"),
        )
        return dl
    except Exception as e:
        return None

def extract_vehicle_registration_from_abbyy(batch_id: int, document_id: int, abbyy_json: Dict[str, Any]) -> Optional[VehicleRegistration]:
    try:
        documents = abbyy_json.get("Documents", [])
        
        veh_doc = None
        for doc in documents:
            doc_name = doc.get("Name", "").strip()
            if "VehicleRegistration_MasterRecord" in doc_name or doc_name == "VehicleRegistration_MasterRecord":
                veh_doc = doc
                break
        
        if not veh_doc:
            return None
        
        sections = veh_doc.get("Sections", [])
        if not sections:
            return None
        
        fields = sections[0].get("Fields", [])
        
        vin_val = get_field_value(fields, "Vehicle_Identification_Number")
        if not vin_val:
            return None
        
        vehicle = VehicleRegistration(
            batch_id=str(batch_id),
            document_id=str(document_id),
            vin=vin_val,
            license_plate=get_field_value(fields, "Lic_Number"),
            make=get_field_value(fields, "Make"),
            year_model=get_field_value(fields, "Yr_Mdl"),
            year_sold=get_field_value(fields, "Yr_Sold"),
            body_type=get_field_value(fields, "Body_Type_Model"),
            vehicle_class=get_field_value(fields, "Cls"),
            vehicle_type=get_field_value(fields, "Type_Vehicle"),
            type_license=get_field_value(fields, "Type_License"),
            vehicle_use=get_field_value(fields, "Type_Vehicle_Use"),
            certs_typed=get_field_value(fields, "Certs_Typed"),
            registered_owner=get_field_value(fields, "Registered_Owner"),
            date_issued=parse_datetime(get_field_value(fields, "Date_Issued") or ""),
            expiration_date=parse_datetime(get_field_value(fields, "Expiration_Date") or ""),
            date_received=parse_datetime(get_field_value(fields, "Date_Received") or ""),
            pic=get_field_value(fields, "Pic"),
            cc_alco=get_field_value(fields, "Cc_Alco"),
            amount_paid=get_field_value(fields, "Amount_Paid"),
            lien_holder=get_field_value(fields, "Lien_Holder"),
        )
        return vehicle
    except Exception as e:
        return None

def save_driver_license(db: Session, dl: DriverLicense) -> DriverLicense:
    db.add(dl)
    db.commit()
    db.refresh(dl)
    return dl

def save_vehicle_registration(db: Session, vehicle: VehicleRegistration) -> VehicleRegistration:
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

def extract_and_store_abbyy_response(db: Session, batch_id: int, abbyy_json: Dict[str, Any]) -> Dict[str, Any]:
    results = {
        "batch_id": batch_id,
        "driver_licenses": [],
        "vehicles": [],
        "errors": []
    }
    
    documents = abbyy_json.get("Documents", [])
    
    for doc in documents:
        doc_id = doc.get("DocumentId")
        doc_name = doc.get("Name", "").strip()
        
        try:
            if "DriverLicense_LeadSheet" in doc_name:
                dl = extract_driver_license_from_abbyy(batch_id, doc_id, abbyy_json)
                if dl:
                    saved_dl = save_driver_license(db, dl)
                    results["driver_licenses"].append({
                        "id": saved_dl.id,
                        "name": f"{saved_dl.first_first_name} {saved_dl.first_last_name}",
                        "license": saved_dl.tn_dl,
                        "expiration": saved_dl.expiration_date.isoformat() if saved_dl.expiration_date else None
                    })
            
            elif "VehicleRegistration_MasterRecord" in doc_name:
                vehicle = extract_vehicle_registration_from_abbyy(batch_id, doc_id, abbyy_json)
                if vehicle:
                    saved_vehicle = save_vehicle_registration(db, vehicle)
                    results["vehicles"].append({
                        "id": saved_vehicle.id,
                        "vin": saved_vehicle.vin,
                        "make": saved_vehicle.make,
                        "plate": saved_vehicle.license_plate,
                        "expiration": saved_vehicle.expiration_date.isoformat() if saved_vehicle.expiration_date else None
                    })
        except Exception as e:
            results["errors"].append({
                "document_id": doc_id,
                "document_name": doc_name,
                "error": str(e)
            })
    
    return results