import json, sqlite3
from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db
from .auth import current_user, login_required, roles_required

STATUSES = ["Recebido", "Em preparação", "Pronto para retirada", "Saiu para entrega", "Finalizado", "Cancelado"]

def register_routes(app):
    @app.teardown_appcontext
    def close_connection(error): 
        from .db import close_db
        close_db(error)

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user(), "cart_count": sum(int(x.get("qty",1)) for x in session.get("cart",[]))}

    def get_setting(key, default=None):
        row = get_db().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def business_open():
        hours = json.loads(get_setting("opening_hours", "{}"))
        day = ["mon","tue","wed","thu","fri","sat","sun"][datetime.now().weekday()]
        span = hours.get(day, "Fechado")
        if span == "Fechado": return False
        try:
            start,end = span.split("-")
            now = datetime.now().strftime("%H:%M")
            return start <= now <= end
        except Exception: return True

    @app.get("/")
    def home():
        products = get_db().execute("SELECT * FROM products WHERE active=1 ORDER BY id LIMIT 4").fetchall()
        return render_template("index.html", products=products, is_open=business_open())

    @app.get("/sobre")
    def about():
        return render_template("about.html", is_open=business_open())

    @app.get("/cardapio")
    def menu():
        category = request.args.get("categoria", "Todos")
        categories = ["Todos","Clássicos","Especiais","Premium","Veganos"]
        sql = "SELECT * FROM products WHERE active=1"
        args = []
        if category != "Todos" and category in categories:
            sql += " AND category=?"; args.append(category)
        products = get_db().execute(sql+" ORDER BY category,name", args).fetchall()
        return render_template("menu.html", products=products, categories=categories, selected=category, is_open=business_open())

    @app.route("/cadastro", methods=["GET","POST"])
    def register():
        if request.method == "POST":
            name,email,password = request.form.get("name","").strip(),request.form.get("email","").strip().lower(),request.form.get("password","")
            if not name or not email or len(password)<6:
                flash("Preencha os campos. A senha precisa ter pelo menos 6 caracteres.", "danger")
            else:
                try:
                    cur=get_db().execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",(name,email,generate_password_hash(password)))
                    get_db().commit(); session["user_id"]=cur.lastrowid
                    flash("Conta criada. Boas-vindas!", "success")
                    return redirect(url_for("menu"))
                except sqlite3.IntegrityError:
                    flash("Este e-mail já está cadastrado.", "danger")
        return render_template("auth.html", mode="register")

    @app.route("/entrar", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            email=request.form.get("email","").strip().lower()
            user=get_db().execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
            if user and check_password_hash(user["password_hash"],request.form.get("password","")):
                session.clear(); session["user_id"]=user["id"]
                flash("Login realizado.", "success")
                return redirect(url_for("admin_dashboard") if user["role"] in ("admin","staff") else url_for("menu"))
            flash("E-mail ou senha incorretos.", "danger")
        return render_template("auth.html", mode="login")

    @app.get("/sair")
    def logout():
        session.clear(); flash("Você saiu da sua conta.", "success"); return redirect(url_for("home"))

    def cart_items():
        cart=session.get("cart",[])
        result=[]; subtotal=0
        for i,item in enumerate(cart):
            p=get_db().execute("SELECT * FROM products WHERE id=? AND active=1",(item["product_id"],)).fetchone()
            if not p: continue
            qty=max(1,min(50,int(item.get("qty",1))))
            custom=item.get("customizations",[])
            unit=float(p["price"])+len(custom)*1.0
            result.append({"index":i,"product":p,"qty":qty,"custom":custom,"unit":unit,"line":unit*qty})
            subtotal += unit*qty
        return result,subtotal

    @app.post("/carrinho/adicionar/<int:product_id>")
    def add_cart(product_id):
        p=get_db().execute("SELECT * FROM products WHERE id=? AND active=1",(product_id,)).fetchone()
        if not p: abort(404)
        try: qty=max(1,min(50,int(request.form.get("qty",1))))
        except: qty=1
        custom=[x for x in request.form.getlist("ingredients") if x in json.loads(p["ingredients"])]
        cart=session.get("cart",[])
        cart.append({"product_id":product_id,"qty":qty,"customizations":custom})
        session["cart"]=cart
        flash(f"{p['name']} adicionado ao carrinho.", "success")
        return redirect(request.referrer or url_for("menu"))

    @app.get("/carrinho")
    def cart():
        items,subtotal=cart_items()
        return render_template("cart.html", items=items, subtotal=subtotal)

    @app.post("/carrinho/atualizar")
    def update_cart():
        cart=session.get("cart",[])
        for i,item in enumerate(cart):
            try: item["qty"]=max(1,min(50,int(request.form.get(f"qty_{i}",item.get("qty",1)))))
            except: pass
        session["cart"]=cart
        return redirect(url_for("cart"))

    @app.post("/carrinho/remover/<int:index>")
    def remove_cart(index):
        cart=session.get("cart",[])
        if 0<=index<len(cart): cart.pop(index)
        session["cart"]=cart
        return redirect(url_for("cart"))

    @app.route("/finalizar", methods=["GET","POST"])
    @login_required
    def checkout():
        items,subtotal=cart_items()
        if not items:
            flash("Seu carrinho está vazio.", "warning"); return redirect(url_for("menu"))
        if request.method=="POST":
            name=request.form.get("name",current_user()["name"]).strip()
            phone=request.form.get("phone","").strip()
            fulfillment=request.form.get("fulfillment","retirada")
            address=request.form.get("address","").strip()
            payment=request.form.get("payment","pix")
            notes=request.form.get("notes","").strip()
            code=request.form.get("coupon","").strip().upper()
            if not name or not phone or fulfillment not in ("retirada","entrega") or payment not in ("pix","cartao") or (fulfillment=="entrega" and not address):
                flash("Confira nome, telefone, modalidade e endereço quando houver entrega.", "danger")
                return render_template("checkout.html",items=items,subtotal=subtotal)
            discount=0; coupon_code=None
            if code:
                coupon=get_db().execute("SELECT * FROM coupons WHERE code=? AND active=1",(code,)).fetchone()
                if not coupon or (coupon["expires_at"] and coupon["expires_at"] < datetime.now().strftime("%Y-%m-%d")) or subtotal < coupon["min_total"]:
                    flash("Cupom inválido, expirado ou não atingiu o valor mínimo.", "danger")
                    return render_template("checkout.html",items=items,subtotal=subtotal)
                discount=min(subtotal, subtotal*coupon["value"]/100 if coupon["kind"]=="percent" else coupon["value"])
                coupon_code=code
            total=round(subtotal-discount,2)
            db=get_db()
            cur=db.execute("""INSERT INTO orders(user_id,customer_name,phone,fulfillment,address,payment,subtotal,discount,total,coupon_code,notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(current_user()["id"],name,phone,fulfillment,address,payment,subtotal,discount,total,coupon_code,notes))
            oid=cur.lastrowid
            for item in items:
                db.execute("""INSERT INTO order_items(order_id,product_id,product_name,quantity,unit_price,customizations)
                    VALUES(?,?,?,?,?,?)""",(oid,item["product"]["id"],item["product"]["name"],item["qty"],item["unit"],json.dumps(item["custom"],ensure_ascii=False)))
            db.commit(); session["cart"]=[]
            flash("Pedido enviado à cafeteria!", "success")
            return redirect(url_for("track_order",order_id=oid))
        return render_template("checkout.html",items=items,subtotal=subtotal)

    @app.get("/pedido/<int:order_id>")
    @login_required
    def track_order(order_id):
        order=get_db().execute("SELECT * FROM orders WHERE id=? AND user_id=?",(order_id,current_user()["id"])).fetchone()
        if not order: abort(404)
        lines=get_db().execute("SELECT * FROM order_items WHERE order_id=?",(order_id,)).fetchall()
        review=get_db().execute("SELECT * FROM reviews WHERE order_id=?",(order_id,)).fetchone()
        return render_template("track.html",order=order,lines=lines,review=review)

    @app.get("/api/pedido/<int:order_id>")
    @login_required
    def order_status_api(order_id):
        order=get_db().execute("SELECT status FROM orders WHERE id=? AND user_id=?",(order_id,current_user()["id"])).fetchone()
        if not order: abort(404)
        return jsonify({"status":order["status"]})

    @app.get("/favoritos")
    @login_required
    def favorites():
        products=get_db().execute("""SELECT p.* FROM products p JOIN favorites f ON f.product_id=p.id
            WHERE f.user_id=? AND p.active=1 ORDER BY p.name""",(current_user()["id"],)).fetchall()
        return render_template("favorites.html",products=products)

    @app.post("/favoritos/<int:product_id>")
    @login_required
    def toggle_favorite(product_id):
        db=get_db()
        exists=db.execute("SELECT 1 FROM favorites WHERE user_id=? AND product_id=?",(current_user()["id"],product_id)).fetchone()
        if exists: db.execute("DELETE FROM favorites WHERE user_id=? AND product_id=?",(current_user()["id"],product_id))
        else:
            if db.execute("SELECT 1 FROM products WHERE id=? AND active=1",(product_id,)).fetchone():
                db.execute("INSERT OR IGNORE INTO favorites(user_id,product_id) VALUES(?,?)",(current_user()["id"],product_id))
        db.commit(); return redirect(request.referrer or url_for("favorites"))

    @app.get("/historico")
    @login_required
    def history():
        orders=get_db().execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC",(current_user()["id"],)).fetchall()
        return render_template("history.html",orders=orders)

    @app.post("/pedido/<int:order_id>/avaliar")
    @login_required
    def review_order(order_id):
        order=get_db().execute("SELECT * FROM orders WHERE id=? AND user_id=?",(order_id,current_user()["id"])).fetchone()
        if not order or order["status"]!="Finalizado": abort(400)
        try: rating=max(1,min(5,int(request.form.get("rating",5))))
        except: rating=5
        comment=request.form.get("comment","").strip()[:1000]
        try:
            get_db().execute("INSERT INTO reviews(order_id,user_id,rating,comment) VALUES(?,?,?,?)",(order_id,current_user()["id"],rating,comment))
            get_db().commit(); flash("Obrigado pela avaliação!", "success")
        except sqlite3.IntegrityError: flash("Este pedido já foi avaliado.", "warning")
        return redirect(url_for("track_order",order_id=order_id))

    # ADMIN / ATENDENTE
    @app.get("/admin")
    @roles_required("admin","staff")
    def admin_dashboard():
        db=get_db()
        stats={
          "today":db.execute("SELECT COUNT(*) n FROM orders WHERE date(created_at)=date('now','localtime')").fetchone()["n"],
          "pending":db.execute("SELECT COUNT(*) n FROM orders WHERE status IN ('Recebido','Em preparação')").fetchone()["n"],
          "sales":db.execute("SELECT COALESCE(SUM(total),0) n FROM orders WHERE status!='Cancelado' AND date(created_at)=date('now','localtime')").fetchone()["n"]
        }
        recent=db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 8").fetchall()
        return render_template("admin/dashboard.html",stats=stats,recent=recent)

    @app.get("/admin/pedidos")
    @roles_required("admin","staff")
    def admin_orders():
        status=request.args.get("status","")
        sql="SELECT * FROM orders"; args=[]
        if status in STATUSES: sql+=" WHERE status=?"; args.append(status)
        orders=get_db().execute(sql+" ORDER BY id DESC",args).fetchall()
        return render_template("admin/orders.html",orders=orders,statuses=STATUSES,selected=status)

    @app.post("/admin/pedido/<int:order_id>/status")
    @roles_required("admin","staff")
    def update_order_status(order_id):
        status=request.form.get("status")
        if status not in STATUSES: abort(400)
        get_db().execute("UPDATE orders SET status=? WHERE id=?",(status,order_id)); get_db().commit()
        flash("Status do pedido atualizado.", "success")
        return redirect(request.referrer or url_for("admin_orders"))

    @app.route("/admin/produtos", methods=["GET","POST"])
    @roles_required("admin")
    def admin_products():
        if request.method=="POST":
            name=request.form.get("name","").strip(); category=request.form.get("category","Clássicos")
            description=request.form.get("description","").strip()
            try: price=float(request.form.get("price","0").replace(",","."))
            except: price=-1
            ingredients=[x.strip() for x in request.form.get("ingredients","").split(",") if x.strip()]
            emoji=request.form.get("emoji","🧁").strip()[:8]
            if not name or price<0:
                flash("Informe nome e preço válido.", "danger")
            else:
                get_db().execute("INSERT INTO products(name,category,description,price,ingredients,image_emoji) VALUES(?,?,?,?,?,?)",
                    (name,category,description,price,json.dumps(ingredients,ensure_ascii=False),emoji))
                get_db().commit(); flash("Produto cadastrado.", "success")
                return redirect(url_for("admin_products"))
        products=get_db().execute("SELECT * FROM products ORDER BY category,name").fetchall()
        return render_template("admin/products.html",products=products)

    @app.route("/admin/produto/<int:product_id>", methods=["GET","POST"])
    @roles_required("admin")
    def edit_product(product_id):
        product=get_db().execute("SELECT * FROM products WHERE id=?",(product_id,)).fetchone()
        if not product: abort(404)
        if request.method=="POST":
            try: price=float(request.form.get("price","0").replace(",","."))
            except: price=-1
            ingredients=[x.strip() for x in request.form.get("ingredients","").split(",") if x.strip()]
            if not request.form.get("name","").strip() or price<0:
                flash("Nome e preço válido são obrigatórios.", "danger")
            else:
                get_db().execute("""UPDATE products SET name=?,category=?,description=?,price=?,ingredients=?,image_emoji=?,active=?
                    WHERE id=?""",(request.form["name"].strip(),request.form["category"],request.form.get("description","").strip(),price,
                    json.dumps(ingredients,ensure_ascii=False),request.form.get("emoji","🧁"),1 if request.form.get("active") else 0,product_id))
                get_db().commit(); flash("Produto atualizado.", "success"); return redirect(url_for("admin_products"))
        return render_template("admin/product_form.html",product=product)

    @app.post("/admin/produto/<int:product_id>/excluir")
    @roles_required("admin")
    def delete_product(product_id):
        get_db().execute("UPDATE products SET active=0 WHERE id=?",(product_id,)); get_db().commit()
        flash("Produto desativado. O histórico de pedidos foi preservado.", "success")
        return redirect(url_for("admin_products"))

    @app.route("/admin/cupons", methods=["GET","POST"])
    @roles_required("admin")
    def admin_coupons():
        if request.method=="POST":
            code=request.form.get("code","").strip().upper()
            kind=request.form.get("kind","percent")
            try: value=float(request.form.get("value","0")); minimum=float(request.form.get("min_total","0"))
            except: value=-1; minimum=0
            if not code or kind not in ("percent","fixed") or value<=0 or (kind=="percent" and value>100):
                flash("Confira os dados do cupom.", "danger")
            else:
                try:
                    get_db().execute("INSERT INTO coupons(code,kind,value,min_total,expires_at) VALUES(?,?,?,?,?)",
                        (code,kind,value,minimum,request.form.get("expires_at") or None))
                    get_db().commit(); flash("Cupom criado.", "success")
                except sqlite3.IntegrityError: flash("Esse código já existe.", "danger")
        coupons=get_db().execute("SELECT * FROM coupons ORDER BY id DESC").fetchall()
        return render_template("admin/coupons.html",coupons=coupons)

    @app.post("/admin/cupom/<int:coupon_id>/alternar")
    @roles_required("admin")
    def toggle_coupon(coupon_id):
        get_db().execute("UPDATE coupons SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?",(coupon_id,))
        get_db().commit(); return redirect(url_for("admin_coupons"))

    @app.get("/admin/relatorios")
    @roles_required("admin")
    def reports():
        db=get_db()
        sales=db.execute("""SELECT date(created_at) day,COUNT(*) orders,COALESCE(SUM(total),0) total
            FROM orders WHERE status!='Cancelado' GROUP BY date(created_at) ORDER BY day DESC LIMIT 30""").fetchall()
        best=db.execute("""SELECT product_name,SUM(quantity) quantity FROM order_items
            GROUP BY product_name ORDER BY quantity DESC LIMIT 10""").fetchall()
        ratings=db.execute("SELECT COUNT(*) count,ROUND(AVG(rating),1) average FROM reviews").fetchone()
        return render_template("admin/reports.html",sales=sales,best=best,ratings=ratings)

    @app.route("/admin/horarios", methods=["GET","POST"])
    @roles_required("admin")
    def hours():
        days=[("mon","Segunda"),("tue","Terça"),("wed","Quarta"),("thu","Quinta"),("fri","Sexta"),("sat","Sábado"),("sun","Domingo")]
        data=json.loads(get_setting("opening_hours","{}"))
        if request.method=="POST":
            data={key:request.form.get(key,"Fechado").strip() or "Fechado" for key,_ in days}
            get_db().execute("INSERT OR REPLACE INTO settings(key,value) VALUES('opening_hours',?)",(json.dumps(data,ensure_ascii=False),))
            get_db().commit(); flash("Horários atualizados.", "success")
        return render_template("admin/hours.html",days=days,data=data)

    @app.get("/admin/avaliacoes")
    @roles_required("admin","staff")
    def admin_reviews():
        reviews=get_db().execute("""SELECT r.*,u.name customer,o.id order_id FROM reviews r
            JOIN users u ON u.id=r.user_id JOIN orders o ON o.id=r.order_id ORDER BY r.id DESC""").fetchall()
        return render_template("admin/reviews.html",reviews=reviews)
