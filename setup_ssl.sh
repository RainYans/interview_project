#!/bin/bash

echo "开始配置自签名HTTPS证书..."

# 创建证书目录
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

echo "生成私钥..."
# 生成私钥
sudo openssl genrsa -out /etc/ssl/private/nginx-selfsigned.key 2048

echo "创建证书配置文件..."
# 生成证书签名请求配置文件（替换为你的实际IP）
sudo tee /etc/ssl/certs/selfsigned.conf > /dev/null <<EOF
[req]
default_bits = 2048
prompt = no
distinguished_name = req_distinguished_name
x509_extensions = v3_req

[req_distinguished_name]
C = CN
ST = Beijing
L = Beijing
O = Interview App
OU = IT Department
CN = 121.40.123.107

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = 121.40.123.107
EOF

echo "生成自签名证书..."
# 生成自签名证书（有效期1年）
sudo openssl req -new -x509 -key /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -days 365 \
    -config /etc/ssl/certs/selfsigned.conf

echo "设置证书权限..."
# 设置正确的权限
sudo chmod 644 /etc/ssl/certs/nginx-selfsigned.crt
sudo chmod 600 /etc/ssl/private/nginx-selfsigned.key

echo "证书生成完成！"
echo "证书位置: /etc/ssl/certs/nginx-selfsigned.crt"
echo "私钥位置: /etc/ssl/private/nginx-selfsigned.key"
echo ""
echo "证书信息："
sudo openssl x509 -in /etc/ssl/certs/nginx-selfsigned.crt -text -noout | grep -A 3 "Subject:"
echo ""
echo "下一步：更新nginx配置并重启容器"