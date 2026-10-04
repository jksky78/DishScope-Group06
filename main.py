
# ---- new lines below ---- (edit_review route)
@app.route("/review/<int:review_id>/edit", methods=["POST"])
def edit_review(review_id):
    user_id = session.get('user_id')

    # Connect to dish database and fetch the review to verify ownership
    conn = sqlite3.connect("dish_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    review = cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()

    if not review:
        conn.close()
        flash_once("Review not found.", "danger")
        return redirect(url_for('dish_view'))

    dish_id = review['dish_id']

    # Only the student who posted the review is allowed to edit it
    if review['user_id'] != user_id:
        conn.close()
        flash_once("You can only edit your own reviews.", "danger")
        return redirect(url_for('dish_detail', dish_id=dish_id))

    rating  = request.form.get('rating')
    comment = request.form.get('comment')

    if not rating:
        conn.close()
        flash_once("Please select a star rating!", "danger")
        return redirect(url_for('dish_detail', dish_id=dish_id))

    # Update timestamp to Malaysia time (UTC+8) so date_posted reflects the edit
    malaysia_time = timezone(timedelta(hours=8))
    date_edit = datetime.now(malaysia_time).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE reviews
        SET rating = ?, comment = ?, date_posted = ?
        WHERE id = ? AND user_id = ?
    """, (int(rating), comment, date_edit, review_id, user_id))

    conn.commit()
    conn.close()
    flash_once("Review updated successfully!", "success")
    return redirect(url_for('dish_detail', dish_id=dish_id))
# ---- end new lines (edit_review) ----

# ---- new lines below ---- (delete_review route)
@app.route("/review/<int:review_id>/delete", methods=["POST"])
def delete_review(review_id):
    user_id = session.get('user_id')

    # Connect to dish database and fetch the review to verify ownership
    conn = sqlite3.connect("dish_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    review = cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()

    if not review:
        conn.close()
        flash_once("Review not found.", "danger")
        return redirect(url_for('dish_view'))

    dish_id = review['dish_id']

    # Only the student who posted the review is allowed to delete it
    if review['user_id'] != user_id:
        conn.close()
        flash_once("You can only delete your own reviews.", "danger")
        return redirect(url_for('dish_detail', dish_id=dish_id))

    cursor.execute("DELETE FROM reviews WHERE id = ? AND user_id = ?", (review_id, user_id))
    conn.commit()
    conn.close()
    flash_once("Review deleted successfully!", "success")
    return redirect(url_for('dish_detail', dish_id=dish_id))
# ---- end new lines (delete_review) ----

