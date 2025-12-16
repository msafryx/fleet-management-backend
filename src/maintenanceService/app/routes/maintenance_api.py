"""
Flask-RESTX API Routes with Swagger Documentation
Provides OpenAPI/Swagger UI for the Maintenance Service
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from app.utils.auth import require_auth
from app.services.maintainance_service import MaintenanceService
from app.schemas.maintainance_schema import (
    MaintenanceItemCreateSchema,
    MaintenanceItemUpdateSchema,
    TechnicianSchema,
    TechnicianCreateSchema,
    TechnicianUpdateSchema,
    PartSchema,
    PartCreateSchema,
    PartUpdateSchema,
    RecurringScheduleSchema,
    RecurringScheduleCreateSchema,
    RecurringScheduleUpdateSchema
)
from marshmallow import ValidationError

# Create API namespace
api = Namespace('maintenance', description='Maintenance management operations')

# ==================== Swagger Models ====================

# Maintenance Item Model (for responses)
maintenance_item_model = api.model('MaintenanceItem', {
    'id': fields.String(required=True, description='Maintenance item ID', example='M001'),
    'vehicle_id': fields.String(required=True, description='Vehicle ID', example='VH-001'),
    'type': fields.String(required=True, description='Maintenance type', example='Oil Change'),
    'description': fields.String(description='Detailed description', example='Regular oil and filter change'),
    'status': fields.String(required=True, description='Current status', 
                           enum=['overdue', 'due_soon', 'scheduled', 'in_progress', 'completed', 'cancelled'],
                           example='scheduled'),
    'priority': fields.String(required=True, description='Priority level',
                             enum=['low', 'medium', 'high', 'critical'],
                             example='medium'),
    'due_date': fields.Date(required=True, description='Due date', example='2024-12-31'),
    'scheduled_date': fields.DateTime(description='Scheduled date and time'),
    'completed_date': fields.DateTime(description='Completion date and time'),
    'current_mileage': fields.Integer(required=True, description='Current vehicle mileage', example=45000),
    'due_mileage': fields.Integer(required=True, description='Mileage when maintenance is due', example=50000),
    'estimated_cost': fields.Float(description='Estimated cost', example=150.50),
    'actual_cost': fields.Float(description='Actual cost after completion', example=175.00),
    'assigned_to': fields.String(description='Service center or technician', example='Service Center A'),
    'assigned_technician': fields.String(description='Assigned technician name'),
    'notes': fields.String(description='Additional notes'),
    'parts_needed': fields.Raw(description='JSON list of required parts'),
    'attachments': fields.Raw(description='JSON list of attachment URLs'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
})

# Create Model (for POST requests)
maintenance_create_model = api.model('MaintenanceCreate', {
    'id': fields.String(required=True, description='Unique maintenance item ID', example='M006'),
    'vehicle_id': fields.String(required=True, description='Vehicle ID', example='VH-001'),
    'type': fields.String(required=True, description='Maintenance type', example='Oil Change'),
    'description': fields.String(description='Detailed description'),
    'status': fields.String(description='Initial status', example='scheduled'),
    'priority': fields.String(description='Priority level', example='medium'),
    'due_date': fields.Date(required=True, description='Due date', example='2024-12-31'),
    'current_mileage': fields.Integer(required=True, description='Current mileage', example=45000),
    'due_mileage': fields.Integer(required=True, description='Mileage when due', example=50000),
    'estimated_cost': fields.Float(description='Estimated cost', example=150.50),
    'assigned_to': fields.String(description='Service center', example='Service Center A'),
    'assigned_technician': fields.String(description='Technician name'),
    'notes': fields.String(description='Additional notes'),
})

# Update Model (for PUT/PATCH requests)
maintenance_update_model = api.model('MaintenanceUpdate', {
    'type': fields.String(description='Maintenance type'),
    'description': fields.String(description='Detailed description'),
    'status': fields.String(description='Status'),
    'priority': fields.String(description='Priority level'),
    'due_date': fields.Date(description='Due date'),
    'scheduled_date': fields.DateTime(description='Scheduled date'),
    'completed_date': fields.DateTime(description='Completion date'),
    'current_mileage': fields.Integer(description='Current mileage'),
    'due_mileage': fields.Integer(description='Mileage when due'),
    'estimated_cost': fields.Float(description='Estimated cost'),
    'actual_cost': fields.Float(description='Actual cost'),
    'assigned_to': fields.String(description='Service center'),
    'assigned_technician': fields.String(description='Technician name'),
    'notes': fields.String(description='Additional notes'),
    'parts_needed': fields.Raw(description='Required parts'),
    'attachments': fields.Raw(description='Attachments'),
})

# Pagination Model
pagination_model = api.model('PaginatedMaintenanceItems', {
    'items': fields.List(fields.Nested(maintenance_item_model), description='List of maintenance items'),
    'total': fields.Integer(description='Total number of items'),
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page'),
    'pages': fields.Integer(description='Total number of pages'),
})

# Summary Model
summary_model = api.model('MaintenanceSummary', {
    'total_items': fields.Integer(description='Total maintenance items'),
    'by_status': fields.Raw(description='Count by status'),
    'by_priority': fields.Raw(description='Count by priority'),
    'total_estimated_cost': fields.Float(description='Total estimated costs'),
    'total_actual_cost': fields.Float(description='Total actual costs'),
    'overdue_count': fields.Integer(description='Number of overdue items'),
    'due_soon_count': fields.Integer(description='Number of items due soon'),
})

# Error Model
error_model = api.model('Error', {
    'error': fields.String(description='Error message'),
    'errors': fields.Raw(description='Validation errors'),
})

# Technician Model
technician_model = api.model('Technician', {
    'id': fields.String(description='Technician ID'),
    'name': fields.String(description='Technician Name'),
    'email': fields.String(description='Email Address'),
    'phone': fields.String(description='Phone Number'),
    'specialization': fields.List(fields.String, description='List of specializations'),
    'status': fields.String(description='Status'),
    'rating': fields.Float(description='Rating'),
    'completed_jobs': fields.Integer(description='Completed Jobs Count'),
    'active_jobs': fields.Integer(description='Active Jobs Count'),
    'certifications': fields.List(fields.String, description='Certifications'),
    'hourly_rate': fields.Float(description='Hourly Rate'),
    'join_date': fields.String(description='Join Date'),
    'created_at': fields.String(description='Created At'),
    'updated_at': fields.String(description='Updated At'),
})

technician_create_model = api.model('TechnicianCreate', {
    'name': fields.String(required=True),
    'email': fields.String(required=True),
    'phone': fields.String(required=True),
    'specialization': fields.List(fields.String),
    'status': fields.String(),
    'certifications': fields.List(fields.String),
    'hourly_rate': fields.Float(required=True),
    'join_date': fields.Date(),
})

technician_update_model = api.model('TechnicianUpdate', {
    'name': fields.String(),
    'email': fields.String(),
    'phone': fields.String(),
    'specialization': fields.List(fields.String),
    'status': fields.String(),
    'rating': fields.Float(),
    'completed_jobs': fields.Integer(),
    'active_jobs': fields.Integer(),
    'certifications': fields.List(fields.String),
    'hourly_rate': fields.Float(),
})

# Part Model
part_model = api.model('Part', {
    'id': fields.String(description='Part ID'),
    'name': fields.String(description='Part Name'),
    'part_number': fields.String(description='Part Number'),
    'category': fields.String(description='Category'),
    'quantity': fields.Integer(description='Quantity in stock'),
    'min_quantity': fields.Integer(description='Minimum quantity'),
    'unit_cost': fields.Float(description='Unit cost'),
    'supplier': fields.String(description='Supplier'),
    'location': fields.String(description='Location'),
    'last_restocked': fields.String(description='Last restocked date'),
    'used_in': fields.List(fields.String, description='Used in maintenance types'),
})

part_create_model = api.model('PartCreate', {
    'name': fields.String(required=True),
    'part_number': fields.String(required=True),
    'category': fields.String(required=True),
    'quantity': fields.Integer(required=True),
    'min_quantity': fields.Integer(required=True),
    'unit_cost': fields.Float(required=True),
    'supplier': fields.String(),
    'location': fields.String(),
    'used_in': fields.List(fields.String),
})

part_update_model = api.model('PartUpdate', {
    'name': fields.String(),
    'part_number': fields.String(),
    'category': fields.String(),
    'quantity': fields.Integer(),
    'min_quantity': fields.Integer(),
    'unit_cost': fields.Float(),
    'supplier': fields.String(),
    'location': fields.String(),
    'used_in': fields.List(fields.String),
})

# Recurring Schedule Model
recurring_schedule_model = api.model('RecurringSchedule', {
    'id': fields.String(description='Schedule ID'),
    'name': fields.String(description='Schedule Name'),
    'vehicle_id': fields.String(description='Vehicle ID'),
    'maintenance_type': fields.String(description='Maintenance Type'),
    'description': fields.String(description='Description'),
    'frequency': fields.String(description='Frequency'),
    'frequency_value': fields.Integer(description='Frequency Value'),
    'estimated_cost': fields.Float(description='Estimated Cost'),
    'estimated_duration': fields.Float(description='Estimated Duration'),
    'assigned_to': fields.String(description='Assigned To'),
    'is_active': fields.Boolean(description='Is Active'),
    'last_executed': fields.String(description='Last Executed'),
    'next_scheduled': fields.String(description='Next Scheduled'),
    'total_executions': fields.Integer(description='Total Executions'),
    'created_date': fields.String(description='Created Date'),
})

recurring_schedule_create_model = api.model('RecurringScheduleCreate', {
    'name': fields.String(required=True),
    'vehicle_id': fields.String(required=True),
    'maintenance_type': fields.String(required=True),
    'description': fields.String(),
    'frequency': fields.String(required=True),
    'frequency_value': fields.Integer(required=True),
    'estimated_cost': fields.Float(),
    'estimated_duration': fields.Float(),
    'assigned_to': fields.String(),
    'is_active': fields.Boolean(),
})

recurring_schedule_update_model = api.model('RecurringScheduleUpdate', {
    'name': fields.String(),
    'description': fields.String(),
    'frequency': fields.String(),
    'frequency_value': fields.Integer(),
    'estimated_cost': fields.Float(),
    'estimated_duration': fields.Float(),
    'assigned_to': fields.String(),
    'is_active': fields.Boolean(),
})

# ==================== API Resources ====================

@api.route('/')
class MaintenanceList(Resource):
    @api.doc('list_maintenance_items',
             params={
                 'page': 'Page number (default: 1)',
                 'per_page': 'Items per page (default: 10)',
                 'vehicle': 'Filter by vehicle ID',
                 'status': 'Filter by status (can specify multiple)',
                 'priority': 'Filter by priority (can specify multiple)',
                 'assignedTo': 'Filter by assignment'
             })
    @api.marshal_with(pagination_model, code=200, description='Success')
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def get(self):
        """List all maintenance items with optional filtering and pagination"""
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
            return result, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('create_maintenance_item')
    @api.expect(maintenance_create_model, validate=True)
    @api.marshal_with(maintenance_item_model, code=201, description='Created')
    @api.response(400, 'Validation Error', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def post(self):
        """Create a new maintenance item"""
        try:
            schema = MaintenanceItemCreateSchema()
            data = schema.load(request.json)
            
            item = MaintenanceService.create_maintenance_item(data)
            return item.to_dict(), 201
        
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/<string:item_id>')
@api.param('item_id', 'The maintenance item identifier')
class MaintenanceItem(Resource):
    @api.doc('get_maintenance_item')
    @api.marshal_with(maintenance_item_model, code=200, description='Success')
    @api.response(404, 'Maintenance item not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def get(self, item_id):
        """Get a specific maintenance item by ID"""
        try:
            item = MaintenanceService.get_maintenance_item(item_id)
            if not item:
                api.abort(404, f'Maintenance item {item_id} not found')
            
            return item.to_dict(), 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('update_maintenance_item')
    @api.expect(maintenance_update_model, validate=True)
    @api.marshal_with(maintenance_item_model, code=200, description='Success')
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Maintenance item not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def put(self, item_id):
        """Update a maintenance item (full update)"""
        try:
            schema = MaintenanceItemUpdateSchema()
            data = schema.load(request.json, partial=False)
            
            item = MaintenanceService.update_maintenance_item(item_id, data)
            if not item:
                api.abort(404, f'Maintenance item {item_id} not found')
            
            return item.to_dict(), 200
        
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('partial_update_maintenance_item')
    @api.expect(maintenance_update_model, validate=True)
    @api.marshal_with(maintenance_item_model, code=200, description='Success')
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Maintenance item not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def patch(self, item_id):
        """Partially update a maintenance item"""
        try:
            schema = MaintenanceItemUpdateSchema()
            data = schema.load(request.json, partial=True)
            
            item = MaintenanceService.update_maintenance_item(item_id, data)
            if not item:
                api.abort(404, f'Maintenance item {item_id} not found')
            
            return item.to_dict(), 200
        
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')
    
    @api.doc('delete_maintenance_item')
    @api.response(200, 'Success')
    @api.response(404, 'Maintenance item not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def delete(self, item_id):
        """Delete a maintenance item"""
        try:
            success = MaintenanceService.delete_maintenance_item(item_id)
            if not success:
                api.abort(404, f'Maintenance item {item_id} not found')
            
            return {'message': 'Maintenance item deleted successfully'}, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/summary')
class MaintenanceSummary(Resource):
    @api.doc('get_maintenance_summary')
    @api.marshal_with(summary_model, code=200, description='Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get maintenance summary statistics"""
        try:
            summary = MaintenanceService.get_maintenance_summary()
            return summary, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/vehicle/<string:vehicle_id>/history')
@api.param('vehicle_id', 'The vehicle identifier')
class VehicleHistory(Resource):
    @api.doc('get_vehicle_maintenance_history')
    @api.marshal_list_with(maintenance_item_model, code=200, description='Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self, vehicle_id):
        """Get maintenance history for a specific vehicle"""
        try:
            history = MaintenanceService.get_vehicle_maintenance_history(vehicle_id)
            return history, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/status/update-bulk')
class BulkStatusUpdate(Resource):
    @api.doc('update_statuses_bulk')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Background job endpoint to update maintenance statuses based on due dates"""
        try:
            updated = MaintenanceService.update_maintenance_status_bulk()
            return {
                'message': f'Updated {updated} maintenance items',
                'updated_count': updated
            }, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/analytics/costs')
class MaintenanceCostAnalytics(Resource):
    @api.doc('get_cost_analytics')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get detailed cost analytics for maintenance"""
        try:
            analytics = MaintenanceService.get_cost_analytics()
            return analytics, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/analytics/trends')
class MaintenanceTrends(Resource):
    @api.doc('get_maintenance_trends',
             params={
                 'period': 'Time period: week, month, quarter, year (default: month)',
                 'limit': 'Number of periods to return (default: 12)'
             })
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get maintenance trends over time"""
        try:
            period = request.args.get('period', 'month')
            limit = request.args.get('limit', 12, type=int)
            
            trends = MaintenanceService.get_maintenance_trends(period, limit)
            return trends, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/overdue')
class OverdueMaintenanceList(Resource):
    @api.doc('list_overdue_maintenance')
    @api.marshal_list_with(maintenance_item_model, code=200, description='Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all overdue maintenance items"""
        try:
            items = MaintenanceService.get_overdue_items()
            return items, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/upcoming')
class UpcomingMaintenanceList(Resource):
    @api.doc('list_upcoming_maintenance',
             params={
                 'days': 'Number of days to look ahead (default: 30)'
             })
    @api.marshal_list_with(maintenance_item_model, code=200, description='Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get upcoming maintenance items"""
        try:
            days = request.args.get('days', 30, type=int)
            items = MaintenanceService.get_upcoming_items(days)
            return items, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')


@api.route('/search')
class MaintenanceSearch(Resource):
    @api.doc('search_maintenance',
             params={
                 'q': 'Search query (searches type, description, vehicle_id)',
                 'page': 'Page number (default: 1)',
                 'per_page': 'Items per page (default: 10)'
             })
    @api.marshal_with(pagination_model, code=200, description='Success')
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Search maintenance items by query"""
        try:
            query = request.args.get('q', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            result = MaintenanceService.search_maintenance(query, page, per_page)
            return result, 200
        
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

# ==================== Technician Resources ====================
@api.route('/technicians')
class TechnicianList(Resource):
    @api.doc('list_technicians')
    @api.marshal_list_with(technician_model, code=200)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def get(self):
        """Get all technicians"""
        try:
            technicians = MaintenanceService.get_all_technicians()
            return technicians, 200
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

    @api.doc('create_technician')
    @api.expect(technician_create_model, validate=True)
    @api.marshal_with(technician_model, code=201)
    @api.response(400, 'Validation Error', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def post(self):
        """Create a new technician"""
        try:
            schema = TechnicianCreateSchema()
            data = schema.load(request.json)
            technician = MaintenanceService.create_technician(data)
            return technician.to_dict(), 201
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

@api.route('/technicians/<string:tech_id>')
@api.param('tech_id', 'The technician ID')
class TechnicianItem(Resource):
    @api.doc('update_technician')
    @api.expect(technician_update_model, validate=True)
    @api.marshal_with(technician_model, code=200)
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Technician not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def put(self, tech_id):
        """Update a technician"""
        try:
            schema = TechnicianUpdateSchema()
            data = schema.load(request.json)
            technician = MaintenanceService.update_technician(tech_id, data)
            if not technician:
                api.abort(404, f'Technician {tech_id} not found')
            return technician.to_dict(), 200
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

    @api.doc('delete_technician')
    @api.response(200, 'Success')
    @api.response(404, 'Technician not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def delete(self, tech_id):
        """Delete a technician"""
        try:
            success = MaintenanceService.delete_technician(tech_id)
            if not success:
                api.abort(404, f'Technician {tech_id} not found')
            return {'message': 'Technician deleted successfully'}, 200
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

# ==================== Part Resources ====================
@api.route('/parts')
class PartList(Resource):
    @api.doc('list_parts', params={'q': 'Search query'})
    @api.marshal_list_with(part_model, code=200)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def get(self):
        """Get all parts"""
        try:
            query = request.args.get('q')
            parts = MaintenanceService.get_all_parts(query)
            return parts, 200
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

    @api.doc('create_part')
    @api.expect(part_create_model, validate=True)
    @api.marshal_with(part_model, code=201)
    @api.response(400, 'Validation Error', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def post(self):
        """Create a new part"""
        try:
            schema = PartCreateSchema()
            data = schema.load(request.json)
            part = MaintenanceService.create_part(data)
            return part.to_dict(), 201
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

@api.route('/parts/<string:part_id>')
@api.param('part_id', 'The part ID')
class PartItem(Resource):
    @api.doc('update_part')
    @api.expect(part_update_model, validate=True)
    @api.marshal_with(part_model, code=200)
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Part not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def put(self, part_id):
        """Update a part"""
        try:
            schema = PartUpdateSchema()
            data = schema.load(request.json)
            part = MaintenanceService.update_part(part_id, data)
            if not part:
                api.abort(404, f'Part {part_id} not found')
            return part.to_dict(), 200
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

    @api.doc('delete_part')
    @api.response(200, 'Success')
    @api.response(404, 'Part not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def delete(self, part_id):
        """Delete a part"""
        try:
            success = MaintenanceService.delete_part(part_id)
            if not success:
                api.abort(404, f'Part {part_id} not found')
            return {'message': 'Part deleted successfully'}, 200
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

# ==================== Recurring Schedule Resources ====================
@api.route('/recurring-schedules')
class RecurringScheduleList(Resource):
    @api.doc('list_recurring_schedules')
    @api.marshal_list_with(recurring_schedule_model, code=200)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def get(self):
        """Get all recurring schedules"""
        try:
            schedules = MaintenanceService.get_all_recurring_schedules()
            return schedules, 200
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

    @api.doc('create_recurring_schedule')
    @api.expect(recurring_schedule_create_model, validate=True)
    @api.marshal_with(recurring_schedule_model, code=201)
    @api.response(400, 'Validation Error', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def post(self):
        """Create a new recurring schedule"""
        try:
            schema = RecurringScheduleCreateSchema()
            data = schema.load(request.json)
            schedule = MaintenanceService.create_recurring_schedule(data)
            return schedule.to_dict(), 201
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

@api.route('/recurring-schedules/<string:schedule_id>')
@api.param('schedule_id', 'The schedule ID')
class RecurringScheduleItem(Resource):
    @api.doc('update_recurring_schedule')
    @api.expect(recurring_schedule_update_model, validate=True)
    @api.marshal_with(recurring_schedule_model, code=200)
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Schedule not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def put(self, schedule_id):
        """Update a recurring schedule"""
        try:
            schema = RecurringScheduleUpdateSchema()
            data = schema.load(request.json)
            schedule = MaintenanceService.update_recurring_schedule(schedule_id, data)
            if not schedule:
                api.abort(404, f'Schedule {schedule_id} not found')
            return schedule.to_dict(), 200
        except ValidationError as e:
            api.abort(400, f'Validation error', errors=e.messages)
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

    @api.doc('delete_recurring_schedule')
    @api.response(200, 'Success')
    @api.response(404, 'Schedule not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    @api.response(401, 'Unauthorized')
    @require_auth
    def delete(self, schedule_id):
        """Delete a recurring schedule"""
        try:
            success = MaintenanceService.delete_recurring_schedule(schedule_id)
            if not success:
                api.abort(404, f'Schedule {schedule_id} not found')
            return {'message': 'Schedule deleted successfully'}, 200
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')
