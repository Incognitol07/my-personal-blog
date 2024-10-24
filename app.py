from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from models import db, Post
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


# Home - View All Blog Posts
@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


# Create Blog Post Form
@app.route('/create-post', methods=['GET'])
def create_post_form():
    return render_template('create-post.html')


# Create Blog Post - API
@app.route('/create-post', methods=['POST'])
def create_post():
    data = request.form  # For form data
    if not data['title'] or not data['content'] or not data['category'] or not data['tags']:
        flash("An error occurred. All fields are required.", "error")
        return redirect(url_for('create_post'))
    new_post = Post(
        title=data["title"],
        content=data["content"],
        category=data["category"],
        tags=','.join(data.getlist("tags")),  # Handling comma-separated tags
    )
    db.session.add(new_post)
    db.session.commit()
    flash("Created post successfully", "success")
    return redirect(url_for('home'))


# Read All Blog Posts - API
@app.route('/posts', methods=['GET'])
def get_all_posts():
    posts = Post.query.all()
    posts_list = [
        {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category,
            'tags': post.tags.split(', '),
            'created_at': post.created_at
        } for post in posts
    ]
    return jsonify(posts_list), 200


# Read a Single Blog Post - View
@app.route('/view-post/<int:id>', methods=['GET'])
def view_post(id):
    post = Post.query.get_or_404(id)
    return render_template('view-post.html', post=post)


# Read a Single Blog Post - API
@app.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'category': post.category,
        'tags': post.tags.split(', '),
        'created_at': post.created_at
    }), 200


# Edit Blog Post Form
@app.route('/edit-post/<int:id>', methods=['GET'])
def edit_post_form(id):
    post = Post.query.get_or_404(id)
    return render_template('edit-post.html', post=post)


# Update Blog Post - API
@app.route('/edit-post/<int:id>', methods=['POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    data = request.form

    # Check if required fields are empty
    if not data.get('title') or not data.get('content') or not data.get('category'):
        flash("All fields are required!!", "error")
        return redirect(url_for('edit_post_form', id=id))

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.category = data.get('category', post.category)
    post.tags = ','.join(data.get('tags', '').split(','))

    db.session.commit()
    flash("Updated post successfully", "success")
    return redirect(url_for('home'))



# Delete Blog Post - API
@app.route('/delete-post/<int:id>', methods=['POST'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Deleted post successfully", "success")
    return redirect(url_for('home'))


# Filter Blog Posts by a search term
@app.route('/posts/search', methods=['GET'])
def search_posts():
    term = request.args.get('term', '')
    posts = Post.query.filter(
        Post.title.contains(term) |
        Post.content.contains(term) |
        Post.category.contains(term)
    ).all()
    posts_list = [
        {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category,
            'tags': post.tags.split(','),
            'created_at': post.created_at
        } for post in posts
    ]
    return jsonify(posts_list), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
