from flask import request, render_template, flash
from flask_login import current_user
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.YuShuBook import YuShuBook
from app.libs.helper import is_isbn_or_key
from app.view_models.book import *
from app.view_models.trade import TradeInfo
from app.web import web
from app.forms.book import SearchForm


@web.route('/book/search')
def search():
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():  #验证通过,返回True
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)
        yushu_book = YuShuBook()

        if isbn_or_key == 'isbn':
            yushu_book.search_by_isbn(q)
        else:
            yushu_book.search_by_keyword(q,page)

        books.fill(yushu_book,q)
    else:
        flash('搜索的关键字不符合要求,请重新输入关键字')
        # return json.dumps(books,default=lambda o:o.__dict__)
    return render_template('search_result.html',books=books,form=form)


@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False

    #取书籍详情信息
    yushu_book = YuShuBook()
    yushu_book.search_by_isbn(isbn)
    book = BookViewModel(yushu_book.first)

    if current_user.is_authenticated:
        if Gift.query.filter_by(uid=current_user.id,isbn=isbn,launched=False).first():
            has_in_gifts = True
        if Wish.query.filter_by(uid=current_user.id,isbn=isbn,launched=False).first():
            has_in_wishes = True
    trade_gifts = Gift.query.filter_by(isbn=isbn,launched=False).all()
    trade_wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()

    trade_gifts_model = TradeInfo(trade_gifts)
    trade_wishes_model = TradeInfo(trade_wishes)

    return render_template('book_detail.html',book=book,
                           gifts=trade_gifts_model,wishes=trade_wishes_model,
                           has_in_wishes = has_in_wishes,has_in_gifts = has_in_gifts,
                           )


