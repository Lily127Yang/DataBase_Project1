from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer_auth
import uuid
import pytest
from fe.access import operations
import fe.conf as conf

class TestOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.opera = operations.Operations(conf.URL)
        self.seller_id = "test_operations_seller_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_operations_buyer_{}".format(str(uuid.uuid1()))
        self.store_id = "test_operations_store_{}".format(str(uuid.uuid1()))
        self.seller_password = self.seller_id
        self.buyer_password = self.buyer_id
        self.buyer, self.auth = register_new_buyer_auth(self.buyer_id, self.buyer_password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = self.gen_book.get_seller()
        self.temp_order = None
        yield

    def test_cancel_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.opera.order_cancer(order_id, self.buyer_id, self.buyer_password)
        assert code == 200

    def test_cancel_non_exist_buyer_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel(self.buyer_id + "_x", order_id)
        assert code != 200

    def test_cancel_non_exist_order_id(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel(self.buyer_id, order_id + "_x")
        assert code != 200

    def test_processing_order(self):  # 下单后查询当前订单
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.opera.order_lookup(order_id, self.buyer_id, self.buyer_password)
        assert code == 200

    def test_processing_order_sent(self):  # 发货后查询当前订单
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.opera.set_delivery(order_id, self.store_id, self.seller_id, self.seller_password)
        assert code == 907
        code = self.opera.order_lookup(order_id, self.buyer_id, self.buyer_password)
        assert code == 200

    def test_processing_order_receive(self):  # 收货后查询当前订单，订单依然存在
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(1000000000)
        assert code == 200
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.opera.set_delivery(order_id, self.store_id,self.seller_id,self.seller_password)
        assert code == 200
        code = self.opera.set_receipt(order_id, self.buyer_id, self.buyer_password)
        assert code == 200
        code = self.opera.order_lookup(order_id, self.buyer_id, self.buyer_password)
        assert code == 200

    def test_seller_processing_order_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code = self.buyer.add_funds(1000000000)
        assert code == 200
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.opera.set_delivery(order_id, self.store_id,self.seller_id,self.seller_password)
        assert code == 200
        code = self.opera.order_lookup(order_id, self.seller_id, self.seller_password)
        assert code == 200








