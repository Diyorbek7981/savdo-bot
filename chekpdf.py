from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_order_receipt(order, user, address):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    c.setFont("Helvetica-Bold", 14)
    c.drawString(180, height - 50, f"🧾 BUYURTMA CHEKI No:{order.get('id', '')}")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"👤 Mijoz: {user.get('first_name', '')} (@{user.get('user_name', '')})")
    c.drawString(50, height - 100, f"📞 Telefon: {user.get('phone_number', '❌ Yo‘q')}")
    c.drawString(50, height - 120, f"📍 Manzil: {address}")

    c.line(40, height - 130, width - 40, height - 130)

    y = height - 150
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Mahsulotlar:")
    y -= 20

    c.setFont("Helvetica", 10)
    for item in order.get("items", []):
        name = item["product_name"]
        qty = float(item["quantity"])
        price = float(item["product_price"])
        total = float(item["total_price"])
        c.drawString(50, y, f"• {name} — {qty} x {price:.2f} = {total:.2f} so‘m")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.line(40, y - 5, width - 40, y - 5)
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"💰 Jami summa: {order['total_price']} so‘m")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
