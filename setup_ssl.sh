#!/bin/bash

echo "清理并重新生成SSL证书..."

# 清理旧证书
sudo rm -f /etc/ssl/certs/nginx-selfsigned.crt
sudo rm -f /etc/ssl/private/nginx-selfsigned.key
sudo rm -f /etc/ssl/certs/selfsigned.conf

# 确保目录存在
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

echo "生成新的私钥..."
# 生成私钥
sudo openssl genrsa -out /etc/ssl/private/nginx-selfsigned.key 2048

echo "创建改进的证书配置文件..."
# 生成证书签名请求配置文件
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
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 121.40.123.107
IP.1 = 127.0.0.1
IP.2 = 121.40.123.107
EOF

echo "生成新的自签名证书..."
# 生成自签名证书（有效期1年）
sudo openssl req -new -x509 -key /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -days 365 \
    -config /etc/ssl/certs/selfsigned.conf \
    -extensions v3_req

echo "设置证书权限..."
# 设置正确的权限
sudo chmod 644 /etc/ssl/certs/nginx-selfsigned.crt
sudo chmod 600 /etc/ssl/private/nginx-selfsigned.key

echo "验证证书..."
# 验证证书
echo "证书详细信息："
sudo openssl x509 -in /etc/ssl/certs/nginx-selfsigned.crt -text -noout | grep -A 10 "X509v3 extensions"

echo ""
echo "证书生成完成！"
echo "证书位置: /etc/ssl/certs/nginx-selfsigned.crt"
echo "私钥位置: /etc/ssl/private/nginx-selfsigned.key"
echo ""
echo "现在请检查你的docker-compose.yml文件中的volume配置"