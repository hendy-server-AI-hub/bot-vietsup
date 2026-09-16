import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Thiết lập log để theo dõi hoạt động và bắt lỗi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. Xử lý lệnh /start khi người dùng bắt đầu chat với bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    # Tạo các nút bấm tương tác nhanh
    keyboard = [
        [InlineKeyboardButton("📦 Tra cứu đơn hàng", callback_data="check_order")],
        [InlineKeyboardButton("❓ Câu hỏi thường gặp", callback_data="faq")],
        [InlineKeyboardButton("☎️ Gặp nhân viên hỗ trợ", callback_data="human_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        f"Xin chào **{user_name}**! 👋\n"
        "Chào mừng bạn đến với hệ thống Hỗ trợ khách hàng tự động (VietSup).\n\n"
        "Vui lòng chọn các dịch vụ bên dưới hoặc nhắn trực tiếp nội dung bạn cần hỗ trợ:"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# 2. Xử lý khi người dùng bấm vào các nút tương tác (Inline Buttons)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Xác nhận đã nhận thao tác bấm nút

    if query.data == "check_order":
        await query.edit_message_text(text="📦 Vui lòng nhập mã đơn hàng của bạn theo cú pháp: `/donhang [Mã_đơn]`", parse_mode="Markdown")
    elif query.data == "faq":
        faq_text = (
            "❓ **Câu hỏi thường gặp (FAQ):**\n\n"
            "1. Thời gian làm việc: 8h00 - 22h00 hàng ngày.\n"
            "2. Chính sách đổi trả: Hỗ trợ đổi trả trong vòng 7 ngày.\n"
            "3. Phí vận chuyển: Miễn phí cho đơn hàng từ 500k."
        )
        await query.edit_message_text(text=faq_text, parse_mode="Markdown")
    elif query.data == "human_support":
        await query.edit_message_text(text="☎️ Yêu cầu của bạn đã được chuyển đến nhân viên trực tổng đài. Vui lòng chờ trong giây lát, chúng tôi sẽ phản hồi sớm nhất!")

# 3. Phản hồi tin nhắn văn bản thông thường dựa theo từ khóa
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "giá" in text or "chi phí" in text:
        reply = "💰 Dạ, chi phí dịch vụ bên em phụ thuộc vào gói bạn chọn. Bạn có muốn nhận bảng báo giá chi tiết không ạ?"
    elif "xin chào" in text or "hello" in text:
        reply = "Dạ chào bạn, VietSup có thể giúp gì cho bạn hôm nay ạ?"
    else:
        reply = "Cảm ơn bạn đã nhắn tin. Yêu cầu của bạn đã được ghi nhận, tư vấn viên sẽ phản hồi lại sớm nhất!"

    await update.message.reply_text(reply)

# ==========================================
# KHỞI CHẠY CHƯƠNG TRÌNH CHÍNH
# ==========================================
if __name__ == '__main__':
    # Dán Token của bạn vào đây
    TOKEN = "8574999116:AAF39jSNBiOx-RqIFF08oLxHXqyxsQ9mYqw"
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Đăng ký các trình xử lý sự kiện (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot VietSup đang chạy và sẵn sàng nhận tin nhắn...")
    app.run_polling()import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Thiết lập log để theo dõi hoạt động và bắt lỗi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. Xử lý lệnh /start khi người dùng bắt đầu chat với bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    # Tạo các nút bấm tương tác nhanh
    keyboard = [
        [InlineKeyboardButton("📦 Tra cứu đơn hàng", callback_data="check_order")],
        [InlineKeyboardButton("❓ Câu hỏi thường gặp", callback_data="faq")],
        [InlineKeyboardButton("☎️ Gặp nhân viên hỗ trợ", callback_data="human_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        f"Xin chào **{user_name}**! 👋\n"
        "Chào mừng bạn đến với hệ thống Hỗ trợ khách hàng tự động (VietSup).\n\n"
        "Vui lòng chọn các dịch vụ bên dưới hoặc nhắn trực tiếp nội dung bạn cần hỗ trợ:"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# 2. Xử lý khi người dùng bấm vào các nút tương tác (Inline Buttons)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Xác nhận đã nhận thao tác bấm nút

    if query.data == "check_order":
        await query.edit_message_text(text="📦 Vui lòng nhập mã đơn hàng của bạn theo cú pháp: `/donhang [Mã_đơn]`", parse_mode="Markdown")
    elif query.data == "faq":
        faq_text = (
            "❓ **Câu hỏi thường gặp (FAQ):**\n\n"
            "1. Thời gian làm việc: 8h00 - 22h00 hàng ngày.\n"
            "2. Chính sách đổi trả: Hỗ trợ đổi trả trong vòng 7 ngày.\n"
            "3. Phí vận chuyển: Miễn phí cho đơn hàng từ 500k."
        )
        await query.edit_message_text(text=faq_text, parse_mode="Markdown")
    elif query.data == "human_support":
        await query.edit_message_text(text="☎️ Yêu cầu của bạn đã được chuyển đến nhân viên trực tổng đài. Vui lòng chờ trong giây lát, chúng tôi sẽ phản hồi sớm nhất!")

# 3. Phản hồi tin nhắn văn bản thông thường dựa theo từ khóa
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "giá" in text or "chi phí" in text:
        reply = "💰 Dạ, chi phí dịch vụ bên em phụ thuộc vào gói bạn chọn. Bạn có muốn nhận bảng báo giá chi tiết không ạ?"
    elif "xin chào" in text or "hello" in text:
        reply = "Dạ chào bạn, VietSup có thể giúp gì cho bạn hôm nay ạ?"
    else:
        reply = "Cảm ơn bạn đã nhắn tin. Yêu cầu của bạn đã được ghi nhận, tư vấn viên sẽ phản hồi lại sớm nhất!"

    await update.message.reply_text(reply)

# ==========================================
# KHỞI CHẠY CHƯƠNG TRÌNH CHÍNH
# ==========================================
if __name__ == '__main__':
    # Dán Token của bạn vào đây
    TOKEN = "8574999116:AAF39jSNBiOx-RqIFF08oLxHXqyxsQ9mYqw"
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Đăng ký các trình xử lý sự kiện (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot VietSup đang chạy và sẵn sàng nhận tin nhắn...")
    app.run_polling() 
