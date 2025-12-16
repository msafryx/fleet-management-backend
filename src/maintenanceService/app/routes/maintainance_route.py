from flask import Blueprint, request, jsonify
from app.services.maintainance_service import MaintenanceService
from app.schemas.maintainance_schema import (
    MaintenanceItemSchema,
    MaintenanceItemCreateSchema,
    MaintenanceItemUpdateSchema
)
from marshmallow import ValidationError
from app.utils.auth import require_auth, require_role

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/', methods=['GET'])
@require_auth
def get_maintenance_items():
    """Get all maintenance items with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        filters = {}
        if request.args.get('vehicle'):
            filters['vehicle'] = request.args.get('vehicle')
        if request.args.get('status'):
            filters['status'] = request.args.getlist('status')
        if request.args.get('priority'):
            filters['priority'] = request.args.getlist('priority')
        if request.args.get('assignedTo'):
            filters['assignedTo'] = request.args.get('assignedTo')
        
        result = MaintenanceService.get_all_maintenance_items(filters, page, per_page)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/<item_id>', methods=['GET'])
@require_auth
def get_maintenance_item(item_id):
    """Get a single maintenance item"""
    try:
        item = MaintenanceService.get_maintenance_item(item_id)
        if not item:
            return jsonify({'error': 'Maintenance item not found'}), 404
        
        return jsonify(item.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/', methods=['POST'])
@require_auth
def create_maintenance_item():
    """Create a new maintenance item"""
    try:
        schema = MaintenanceItemCreateSchema()
        data = schema.load(request.json)
        
        item = MaintenanceService.create_maintenance_item(data)
        return jsonify(item.to_dict()), 201
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/<item_id>', methods=['PUT', 'PATCH'])
@require_auth
def update_maintenance_item(item_id):
    """Update a maintenance item"""
    try:
        schema = MaintenanceItemUpdateSchema()
        data = schema.load(request.json, partial=True)
        
        item = MaintenanceService.update_maintenance_item(item_id, data)
        if not item:
            return jsonify({'error': 'Maintenance item not found'}), 404
        
        return jsonify(item.to_dict()), 200
    
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/<item_id>', methods=['DELETE'])
@require_auth
@require_role('fleet-admin')
def delete_maintenance_item(item_id):
    """Delete a maintenance item"""
    try:
        success = MaintenanceService.delete_maintenance_item(item_id)
        if not success:
            return jsonify({'error': 'Maintenance item not found'}), 404
        
        return jsonify({'message': 'Maintenance item deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/summary', methods=['GET'])
@require_auth
def get_maintenance_summary():
    """Get maintenance summary statistics"""
    try:
        summary = MaintenanceService.get_maintenance_summary()
        return jsonify(summary), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/vehicle/<vehicle_id>/history', methods=['GET'])
@require_auth
def get_vehicle_history(vehicle_id):
    """Get maintenance history for a vehicle"""
    try:
        history = MaintenanceService.get_vehicle_maintenance_history(vehicle_id)
        return jsonify(history), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/status/update-bulk', methods=['POST'])
@require_auth
@require_role('fleet-admin')
def update_statuses_bulk():
    """Background job endpoint to update maintenance statuses"""
    try:
        updated = MaintenanceService.update_maintenance_status_bulk()
        return jsonify({
            'message': f'Updated {updated} maintenance items',
            'updated_count': updated
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= app/utils/__init__.py =============
from app.utils.validators import validate_date, validate_mileage

# ============= app/utils/validators.py =============
from datetime import date, datetime

def validate_date(date_str):
    """Validate date string format"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError('Invalid date format. Expected YYYY-MM-DD')

def validate_mileage(current, due):
    """Validate mileage values"""
    if current < 0 or due < 0:
        raise ValueError('Mileage values must be non-negative')
    if due < current:
        raise ValueError('Due mileage must be greater than or equal to current mileage')
    return True
