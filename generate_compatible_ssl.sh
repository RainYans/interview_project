#!/bin/bash

echo "重新生成兼容现代浏览器的SSL证书..."

# 停止容器以避免文件占用
docker-compose down

# 清理旧证书
sudo rm -f /etc/ssl/certs/nginx-selfsigned.crt
sudo rm -f /etc/ssl/private/nginx-selfsigned.key
sudo rm -f /etc/ssl/certs/selfsigned.conf

# 确保目录存在
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

echo "生成新的私钥..."
# 生成2048位RSA私钥
sudo openssl genrsa -out /etc/ssl/private/nginx-selfsigned.key 2048

echo "创建证书配置文件..."
# 创建符合现代浏览器要求的证书配置
sudo tee /etc/ssl/certs/selfsigned.conf > /dev/null <<EOF
[req]
default_bits = 2048
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C = CN
ST = Beijing
L = Beijing
O = Interview App
OU = IT Department
CN = 121.40.123.107

[v3_req]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment, keyAgreement
extendedKeyUsage = critical, serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 121.40.123.107
IP.1 = 127.0.0.1
IP.2 = 121.40.123.107
EOF

echo "生成自签名证书..."
# 生成证书请求
sudo openssl req -new -key /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.csr \
    -config /etc/ssl/certs/selfsigned.conf

# 生成自签名证书
sudo openssl x509 -req -in /etc/ssl/certs/nginx-selfsigned.csr \
    -signkey /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -days 365 \
    -extensions v3_req \
    -extfile /etc/ssl/certs/selfsigned.conf

# 清理临时文件
sudo rm -f /etc/ssl/certs/nginx-selfsigned.csr

echo "设置证书权限..."
sudo chmod 644 /etc/ssl/certs/nginx-selfsigned.crt
sudo chmod 600 /etc/ssl/private/nginx-selfsigned.key

echo "验证证书配置..."
echo "=== 证书详细信息 ==="
sudo openssl x509 -in /etc/ssl/certs/nginx-selfsigned.crt -text -noout | grep -A 20 "X509v3 extensions"

echo ""
echo "=== 证书有效性检查 ==="
sudo openssl x509 -in /etc/ssl/certs/nginx-selfsigned.crt -noout -dates

echo ""
echo "证书重新生成完成！"
echo "证书位置: /etc/ssl/certs/nginx-selfsigned.crt"
echo "私钥位置: /etc/ssl/private/nginx-selfsigned.key"
echo ""
echo "现在重新启动容器..."

# 重新启动容器
docker-compose up -d

echo "容器启动完成，请稍等几秒让服务完全启动..."
sleep 5

echo "测试连接..."
curl -k -I https://121.40.123.107