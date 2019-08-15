"""Handle requests made on reviews"""
import os
from api import create_app, db

@app.route('/api/v2/businesses/<business_id>/reviews',
           methods=['POST'])
@check_json
@token_required
@check_for_login
def add_review_for(current_user, content, business_id):
    """Add a review for a business."""
    message = validator.validate(content, 'review_reg')
    if message:
        return jsonify(message), 400
    to_review = Business.query.filter_by(id=business_id).first()
    if not to_review:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    if to_review.business_owner == current_user.username:
        return jsonify({'msg': 'Reviewing own business not allowed'}), 400
    review = Review(rating=int(str(content['rating']).strip()),
                    body=content['body'].strip(),
                    owner=current_user,
                    review_for=to_review)
    db.session.add(review)
    db.session.commit()
    message = {'msg': 'Review for business id {} by user {} created'.format(
        review.business_id, review.review_owner),
        'details': {'rating': review.rating,
                    'body': review.body}}
    return jsonify(message), 201


@app.route('/api/v2/businesses/<business_id>/reviews',
           methods=['GET'])
def get_reviews_for(business_id):
    """Retrieve all reviews for a single business."""
    business = Business.query.filter_by(id=business_id).first()
    if not business:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    reviews = Review.query.filter_by(business_id=business_id)
    if not reviews.count():
        return jsonify({'msg': 'No reviews for this business'}), 400
    message = {'reviews': [{'rating': review.rating,
                            'body': review.body,
                            'review_by': review.review_owner}
                           for review in reviews],
               'business_id': business.id,
               'business_owner': business.business_owner}
    return jsonify(message), 200
