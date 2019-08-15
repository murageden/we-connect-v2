"""Handle requests made on business routes"""
import os
from api import create_app, db

@app.route('/api/v2/businesses', methods=['POST'])
@check_json
@token_required
@check_for_login
def register_business(current_user, content):
    """Register a business for a user."""
    err_msg = validator.validate(content, 'business_reg')
    if err_msg:
        return jsonify(err_msg), 400
    new_business = Business(name=content['name'].strip(),
                            category=content['category'].strip(),
                            description=content['description'].strip(),
                            location=content['location'].strip(),
                            owner=current_user
                            )
    db.session.add(new_business)
    db.session.commit()
    message = {'msg': "Business id {} created for owner {}".format(
        new_business.id, new_business.business_owner),
        'details': {'name': new_business.name,
                    'category': new_business.category,
                    'description': new_business.description,
                    'location': new_business.location,
                    'owner': new_business.business_owner
                    }}
    return jsonify(message), 201


@app.route('/api/v2/businesses/<business_id>', methods=['PUT'])
@check_json
@token_required
@check_for_login
def update_business(current_user, content, business_id):
    """Update an existing business."""
    message = validator.validate(content, 'business_reg')
    if message:
        return jsonify(message), 400
    to_update = Business.query.filter_by(id=business_id).first()
    if not to_update:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    if not to_update.business_owner == current_user.username:
        return jsonify(
            {'msg': 'You are not allowed to edit this business'}), 403
    Business.query.filter_by(id=business_id).update(
        {
            'name': content['name'].strip(),
            'category': content['category'].strip(),
            'description': content['description'].strip(),
            'location': content['location'].strip(),
        })
    db.session.commit()
    updated_bs = Business.query.filter_by(id=business_id).first()
    message = {'msg': "Business id {} modified for owner {}".format(
        updated_bs.id, updated_bs.business_owner),
        'details': {'name': updated_bs.name,
                    'category': updated_bs.category,
                    'description': updated_bs.description,
                    'location': updated_bs.location,
                    'owner': updated_bs.business_owner,
                    'id': updated_bs.id
                    }}
    return jsonify(message), 201


@app.route('/api/v2/businesses/<business_id>', methods=['DELETE'])
@token_required
@check_for_login
def delete_business(current_user, business_id):
    """Remove an existing business."""
    to_delete = Business.query.filter_by(id=business_id).first()
    if not to_delete:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    if not to_delete.business_owner == current_user.username:
        return jsonify(
            {'msg': 'You are not allowed to delete this business'}), 403
    db.session.delete(to_delete)
    db.session.commit()
    message = {'msg': 'Business id {} for owner {} deleted successfully'.
               format(to_delete.id, to_delete.business_owner),
               'details': {'name': to_delete.name,
                           'category': to_delete.category,
                           'description': to_delete.description,
                           'location': to_delete.location,
                           'owner': to_delete.business_owner,
                           'id': to_delete.id
                           }}
    return jsonify(message), 200


@app.route('/api/v2/businesses/')
def get_all_businesses():
    """Retrieve a list of all registered businesses."""
    page = 1
    limit = 5
    if 'page' in request.args:
        page = request.args.get('page', 1, type=int)
    if 'limit' in request.args:
        limit = request.args.get('limit', 5, type=int)
    businesses = Business.query.filter_by().paginate(
        page, limit, True)
    if not businesses.items:
        return jsonify({'msg': 'No businesses yet'}), 400
    message = {'businesses': [{'name': business.name,
                               'category': business.category,
                               'description': business.description,
                               'id': business.id,
                               'location': business.location,
                               'owner': business.business_owner}
                              for business in businesses.items],
               "per_page": businesses.per_page, "page": businesses.page,
               "total_pages": businesses.pages,
               "total_results": businesses.total}
    return jsonify(message), 200


@app.route('/api/v2/businesses/search', methods=['GET'])
def search_businesses():
    """Retrieve the list of all businesses."""
    name = ""
    location = ""
    category = ""
    page = 1
    limit = 5
    if 'q' in request.args:
        name = request.args.get('q')
    if 'location' in request.args:
        location = request.args.get('location')
    if 'category' in request.args:
        category = request.args.get('category')
    if 'page' in request.args:
        page = request.args.get('page', 1, type=int)
    if 'limit' in request.args:
        limit = request.args.get('limit', 5, type=int)
    businesses = db.session.query(Business).filter(
        Business.name.ilike('%{0}%'.format(name)),
        Business.location.ilike('%{0}%'.format(location)),
        Business.category.ilike('%{0}%'.format(category))).paginate(
        page, limit, True)
    if name == "" and location == "" and category == "":
        businesses = Business.query.filter_by().paginate(
            page, limit, True)
        if not businesses.items:
            return jsonify({'msg': 'No businesses yet'}), 400
    if not len(list(businesses.items)):
        return jsonify({'msg': 'No businesses match this search'}), 400
    message = {'businesses': [{'name': business.name,
                               'category': business.category,
                               'description': business.description,
                               'location': business.location,
                               'id': business.id,
                               'owner': business.business_owner}
                              for business in businesses.items],
               "per_page": businesses.per_page, "page": businesses.page,
               "total_pages": businesses.pages,
               "total_results": businesses.total}
    return jsonify(message), 200


@app.route('/api/v2/businesses/<business_id>', methods=['GET'])
def get_business(business_id):
    """Retrieve a single business."""
    business = Business.query.filter_by(id=business_id).first()
    if not business:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    message = {'msg': 'Business id {} owned by {} retrieved successfully'.
               format(business.id, business.business_owner),
               'details': {'name': business.name,
                           'category': business.category,
                           'description': business.description,
                           'location': business.location,
                           'id': business.id,
                           'owner': business.business_owner
                           }}
    return jsonify(message), 200
