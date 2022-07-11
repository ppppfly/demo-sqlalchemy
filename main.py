from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    username = Column(String(15), nullable=False, unique=True)
    email_addr = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    password = Column(String(25), nullable=False)
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __str__(self):
        return f'User(' \
               f'username={self.username},' \
               f'email_addr={self.email_addr},' \
               f'phone={self.phone},' \
               f'password={self.password},' \
               f')'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    shipped = Column(Boolean(), default=False)

    user = relationship('User', backref=backref('orders', order_by=id))

    def __str__(self):
        return f'Order(' \
               f'user_id={self.user_id},' \
               f'shipped={self.shipped},' \
               f')'


class Cookie(Base):
    __tablename__ = 'cookies'

    id = Column(Integer(), primary_key=True)
    cookie_name = Column(String(50), index=True)
    cookie_recipe_url = Column(String(255))
    cookie_sku = Column(String(55))
    quantity = Column(Integer())
    unit_cost = Column(Numeric(12, 2))
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'Cookie(' \
               f'cookie_name="{self.cookie_name}",' \
               f'cookie_recipe_url="{self.cookie_recipe_url}",' \
               f'cookie_sku="{self.cookie_sku}",' \
               f'quantity={self.quantity},' \
               f'unit_cost={self.unit_cost},' \
               f')'


class LineItems(Base):
    __tablename__ = 'line_items'

    id = Column(Integer(), primary_key=True)
    order_id = Column(Integer(), ForeignKey('orders.id'))
    cookie_id = Column(Integer(), ForeignKey('cookies.id'))
    quantity = Column(Integer())
    extended_cost = Column(Numeric(12, 2))

    order = relationship('Order', backref=backref('line_items', order_by=id))
    cookie = relationship('Cookie', uselist=False)

    def __str__(self):
        return f'LineItems(' \
               f'order_id={self.order_id},' \
               f'cookie_id={self.cookie_id},' \
               f'quantity={self.quantity},' \
               f'extended_cost={self.extended_cost},' \
               f')'


engine = create_engine('sqlite:///demo.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_cookie():
    cc_cookie = Cookie(cookie_name='chocolate chip',
                       cookie_recipe_url='http://some.aweso.me/cookie/recipe.html',
                       cookie_sku='CC01',
                       quantity=12,
                       unit_cost=0.50)
    session.add(cc_cookie)
    session.commit()
    print(cc_cookie.id)


def multiple_insert():
    dcc = Cookie(cookie_name='dark chocolate chip',
                 cookie_recipe_url='http://some.aweso.me/cookie/recipe_dark.html',
                 cookie_sku='CC02',
                 quantity=1,
                 unit_cost=0.75)
    mol = Cookie(cookie_name='molasses',
                 cookie_recipe_url='http://some.aweso.me/cookie/recipe_molasses.html',
                 cookie_sku='MOL01',
                 quantity=1,
                 unit_cost=0.80)

    session.add(dcc)
    session.add(mol)
    session.flush()
    print(dcc.id)
    print(mol.id)


def bulk_save():
    c1 = Cookie(cookie_name='peanut butter',
                cookie_recipe_url='http://some.aweso.me/cookie/peanut.html',
                cookie_sku='PB01',
                quantity=24,
                unit_cost=0.25)
    c2 = Cookie(cookie_name='oatmeal raisin',
                cookie_recipe_url='http://some.okay.me/cookie/raisin.html',
                cookie_sku='EWW01',
                quantity=100,
                unit_cost=1.00)
    session.bulk_save_objects([c1, c2])
    session.commit()
    print(c1.id)


def query_all():
    print(
        session.query(Cookie).all()
    )


def query_loop():
    for cookie in session.query(Cookie):
        print(cookie)


def limit_fields():
    print(
        session.query(
            Cookie.cookie_name, Cookie.quantity
        ).all()
    )


def order_by():
    for cookie in session.query(Cookie).order_by(Cookie.quantity):
        print('{:3} - {}'.format(cookie.quantity, cookie.cookie_name))


def update():
    query = session.query(Cookie)
    cc_cookie = query.filter(Cookie.cookie_name == 'chocolate chip').first()
    cc_cookie.quantity += 1
    session.commit()
    print(cc_cookie.quantity)


def connect():
    query = session.query(Order.id, User.username, User.phone,
                          Cookie.cookie_name, LineItems.quantity,
                          LineItems.extended_cost)
    query = query.join(User).join(LineItems).join(Cookie)
    results = query.filter(User.username == 'cookiemon').all()


if __name__ == '__main__':
    add_cookie()
    multiple_insert()
    bulk_save()
