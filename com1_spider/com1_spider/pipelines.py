import mysql.connector
import time
from .items import Com1SpiderItem

class Com1SpiderPipeline:
    
    def __init__(self):
        db_host = '20.92.115.130'
        db_user = 'common_user'
        db_password = 'FhHOk!nZUUxaO[Ns'
        db_name = 'zotim_dev'

        try:
            self.conn = mysql.connector.connect(host=db_host, 
                                                user=db_user,
                                                password=db_password,
                                                database=db_name,
                                                auth_plugin='mysql_native_password',
                                                port=3306
                                                )
            self.cursor = self.conn.cursor()
            
        except Exception as e:
            time.sleep(10)
            print(e,'\n Database connection failed\ntrying again')
            

    def process_item(self, item, spider):
        name = item.get('Name')
        sku = item.get('SKU')
        price = item.get('Price')
        description = item.get('Description')
        available_qty = item.get('Available_qty')
        brand = item.get('Brand')
        manufacturer_Part_Number = item.get('Manufacturer_Part_Number')
        weight = item.get('Weight')
        specification = item.get('specification')
        image = item.get('image')
        width = item.get('Width')
        height = item.get('Height')
        length = item.get('Length')
        product_page_link=item.get('Product_page_link')
        scrapedDate = item.get('scrapedDate')
        
        try:    
            sql = f"SELECT id FROM products WHERE manufacturerId = '{manufacturer_Part_Number}'"
            
            self.cursor.execute(sql)
            id_list = self.cursor.fetchall()
            id_available = False
            
            if id_list:
                id_available = True
                product_id = id_list[0][0]
               
                # Updating the data in product table
                update_query = f"UPDATE products SET com1price = '{price}',com1quantity='{available_qty}' WHERE manufacturerId = '{manufacturer_Part_Number}'"
                self.cursor.execute(update_query)
                self.conn.commit()
                
                sql = f"SELECT id FROM product_data WHERE productId='{product_id}' and vendorId=31"
                self.cursor.execute(sql)
                records = self.cursor.fetchall()
                if records:
                    # Updating the data in product data table
                    update_query = f"""UPDATE product_data SET 
                                                        vendorId = 31, 
                                                        categoryId = 0, 
                                                        name=%s,
                                                        description=%s,
                                                        specification=%s,
                                                        images=%s,
                                                        length=%s,
                                                        width=%s,
                                                        height=%s,
                                                        weight=%s,
                                                        quantity=%s,
                                                        price=%s,
                                                        scrapedDate=%s,
                                                        product_link=%s
                                                        WHERE productId = '{product_id}' and vendorId=31"""
                    values = (item.get('Name'),
                            item.get('Description'),
                            item.get('specification'),
                            item.get('image'),
                            item.get('Length'),
                            item.get('Width'),
                            item.get('Height'),
                            item.get('Weight'),
                            item.get('Available_qty'),
                            item.get('Price'),
                            item.get('scrapedDate'),
                            item.get('Product_page_link'),
                            )
                    
                    self.cursor.execute(update_query, values)
                    self.conn.commit()
            
                else:
                    insert_query = f"""INSERT INTO product_data(
                                                                productId,
                                                                vendorId, 
                                                                categoryId, 
                                                                name,
                                                                description,
                                                                specification,
                                                                images,
                                                                length,
                                                                width,
                                                                height,
                                                                weight,
                                                                quantity,
                                                                price,
                                                                scrapedDate,
                                                                product_link)
                                                                VALUES (%s,31,0, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    values = (  product_id,
                                item.get('Name'),
                                item.get('Description'),
                                item.get('specification'),
                                item.get('image'),
                                item.get('Length'),
                                item.get('Width'),
                                item.get('Height'),
                                item.get('Weight'),
                                item.get('Available_qty'),
                                item.get('Price'),
                                item.get('scrapedDate'),
                                item.get('Product_page_link')
                    )
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                
            # Checking if brand already exist in brand table
            select_sql = f"SELECT id FROM brands WHERE name = '{brand}'"
            self.cursor.execute(select_sql)
            brand_id_list = self.cursor.fetchall()
            
            if brand_id_list:
                brand_id = brand_id_list[0][0]
            else:
                # inserting new brand
                insert_query = f"INSERT INTO brands (name) VALUES ('{brand}')"
                self.cursor.execute(insert_query)
                self.conn.commit()
                # retriving the inserted brand's id
                brand_id = cursor.lastrowid
            
            
            
            #  checking if record already exists in the vandor_data_table
            vendor_query = f"SELECT ManufacturerID FROM vendor_product_data WHERE ManufacturerID = '{manufacturer_Part_Number}'"
            self.cursor.execute(vendor_query)
            vandor_id_list = self.cursor.fetchall()

            if vandor_id_list:
                vendor_update_query = f"""UPDATE vendor_product_data SET 
                                                    ManufacturerID=%s,
                                                    vendorId = 31, 
                                                    categoryId = 0, 
                                                    brandId=%s,
                                                    name=%s,
                                                    description=%s,
                                                    specification=%s,
                                                    images=%s,
                                                    length=%s,
                                                    width=%s,
                                                    height=%s,
                                                    weight=%s,
                                                    quantity=%s,
                                                    price=%s,
                                                    scrapedDate=%s,
                                                    product_link=%s
                                                    WHERE manufacturerId = '{manufacturer_Part_Number}'"""
                values = (  item.get('Manufacturer_Part_Number'),
                            brand_id,
                            item.get('Name'),
                            item.get('Description'),
                            item.get('specification'),
                            item.get('image'),
                            item.get('Length'),
                            item.get('Width'),
                            item.get('Height'),
                            item.get('Weight'),
                            item.get('Available_qty'),
                            item.get('Price'),
                            item.get('scrapedDate'),
                            item.get('Product_page_link')
                )
                
                self.cursor.execute(vendor_update_query, values)
                self.conn.commit()
            
            else:
                vendor_insert_query = f"""INSERT INTO vendor_product_data(
                                                            ManufacturerID,
                                                            vendorId, 
                                                            categoryId, 
                                                            brandId,
                                                            name,
                                                            description,
                                                            specification,
                                                            images,
                                                            length,
                                                            width,
                                                            height,
                                                            weight,
                                                            quantity,
                                                            price,
                                                            scrapedDate,
                                                            product_link)
                                                            VALUES (%s,31,0, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                values = (  item.get('Manufacturer_Part_Number'),
                            brand_id,
                            item.get('Name'),
                            item.get('Description'),
                            item.get('specification'),
                            item.get('image'),
                            item.get('Length'),
                            item.get('Width'),
                            item.get('Height'),
                            item.get('Weight'),
                            item.get('Available_qty'),
                            item.get('Price'),
                            item.get('scrapedDate'),
                            item.get('Product_page_link')
                )
                self.cursor.execute(vendor_insert_query, values)
                self.conn.commit()
        except Exception as e:
            print(e)
        
        return item
    
    def close_spider(self, spider):
        self.conn.close()
            