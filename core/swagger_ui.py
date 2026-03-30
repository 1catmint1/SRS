from fastapi.responses import HTMLResponse


def get_custom_swagger_ui_html():
    custom_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>系统接口调试文档 (全中文增强版)</title>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style> .topbar { display: none; } </style>
    </head>
    <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
    window.onload = function() {
        const ui = SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
            layout: "BaseLayout"
        });

        setInterval(() => {
            document.querySelectorAll('.auth-container h4').forEach(node => { if(node.innerText.includes('Available authorizations')) node.innerText = '系统可用授权方式'; });
            document.querySelectorAll('.auth-container p').forEach(node => { if(node.innerText.includes('OAuth2')) node.innerText = '身份令牌认证 (OAuth2)'; });
            document.querySelectorAll('.auth-container .btn-done').forEach(node => { if(node.innerText.includes('Close')) node.innerText = '关闭弹窗'; });
            document.querySelectorAll('.auth-container .authorize').forEach(node => { if(node.innerText.includes('Authorize')) node.innerText = '点击进行授权认证'; });
            document.querySelectorAll('.auth-container .logout').forEach(node => { if(node.innerText.includes('Logout')) node.innerText = '注销退出系统'; });

            document.querySelectorAll('.auth-container label').forEach(node => { 
                if(node.innerText.includes('client_id')) node.innerHTML = '客户端帐号 <span style="color:#888;">(选填)</span>';
                if(node.innerText.includes('client_secret')) node.innerHTML = '客户端密钥 <span style="color:#888;">(选填)</span>';
                if(node.innerText.includes('username')) node.innerHTML = '登录用户名 <span style="color:red;">*</span>';
                if(node.innerText.includes('password')) node.innerHTML = '登录密码 <span style="color:red;">*</span>';
            });

            document.querySelectorAll('.btn.execute').forEach(node => { if(node.innerText.includes('Execute')) node.innerText = '🚀 执行接口调用'; });
            document.querySelectorAll('.btn.try-out__btn').forEach(node => { if(node.innerText.includes('Try it out')) node.innerText = '🔓 开启测试模式'; });
            document.querySelectorAll('.btn.try-out__btn.cancel').forEach(node => { if(node.innerText.includes('Cancel')) node.innerText = '取消测试'; });
            document.querySelectorAll('.parameters-col_name').forEach(node => { if(node.innerText === 'Name') node.innerText = '参数名称'; });
            document.querySelectorAll('.parameters-col_description').forEach(node => { if(node.innerText === 'Description') node.innerText = '参数描述与规则'; });
            document.querySelectorAll('.responses-table .response-col_status').forEach(node => { if(node.innerText === 'Code') node.innerText = 'HTTP状态码'; });
            document.querySelectorAll('.responses-table .response-col_description').forEach(node => { if(node.innerText === 'Description') node.innerText = '响应数据结构'; });
        }, 300);
    };
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=custom_html)