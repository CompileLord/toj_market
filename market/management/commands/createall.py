import os
import random
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from market.models import Category, Shop, Product, ImageProduct
from PIL import Image

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовые данные: 6 категорий, 5 магазинов и 20 продуктов'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Начинаем создание тестовых данных...'))
        
        # Создаем категории
        categories = self.create_categories()
        self.stdout.write(self.style.SUCCESS(f'✓ Создано категорий: {len(categories)}'))
        
        # Создаем пользователей-продавцов и магазины
        shops = self.create_shops()
        self.stdout.write(self.style.SUCCESS(f'✓ Создано магазинов: {len(shops)}'))
        
        # Создаем продукты
        products = self.create_products(categories, shops)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано продуктов: {len(products)}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Все данные успешно созданы!'))

    def download_image(self, url, width=800, height=600):
        """Загружает изображение из интернета"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Изменяем размер
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            return ContentFile(buffer.read())
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    Ошибка загрузки изображения: {e}'))
            # Создаем заглушку
            return self.create_placeholder_image(width, height)
    
    def create_placeholder_image(self, width=800, height=600):
        """Создает изображение-заглушку"""
        color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        image = Image.new('RGB', (width, height), color)
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return ContentFile(buffer.read())

    def create_categories(self):
        """Создает 6 категорий с проверкой на существование"""
        category_data = [
            {
                'name': 'Электроника',
                'image': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop'
            },
            {
                'name': 'Одежда',
                'image': 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=400&h=400&fit=crop'
            },
            {
                'name': 'Книги',
                'image': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400&h=400&fit=crop'
            },
            {
                'name': 'Спорт и отдых',
                'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&h=400&fit=crop'
            },
            {
                'name': 'Дом и сад',
                'image': 'https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=400&h=400&fit=crop'
            },
            {
                'name': 'Красота и здоровье',
                'image': 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400&h=400&fit=crop'
            }
        ]
        
        categories = []
        for data in category_data:
            category, created = Category.objects.get_or_create(
                title=data['name'],
                defaults={'is_deleted': False}
            )
            
            if created or not category.avatar:
                # Загружаем изображение для категории
                image_file = self.download_image(data['image'], 400, 400)
                category.avatar.save(f'{data["name"].lower().replace(" ", "_")}.jpg', image_file, save=True)
                self.stdout.write(f'  → Создана категория: {data["name"]}')
            else:
                self.stdout.write(f'  → Категория уже существует: {data["name"]}')
            
            categories.append(category)
        
        return categories

    def create_shops(self):
        """Создает 5 магазинов с продавцами"""
        shop_data = [
            {
                'title': 'TechStore',
                'bio': 'Лучшая электроника по доступным ценам',
                'image': 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&h=400&fit=crop'
            },
            {
                'title': 'FashionHub',
                'bio': 'Модная одежда для всей семьи',
                'image': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&h=400&fit=crop'
            },
            {
                'title': 'BookWorld',
                'bio': 'Огромный выбор книг на любой вкус',
                'image': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=600&h=400&fit=crop'
            },
            {
                'title': 'SportPro',
                'bio': 'Все для спорта и активного отдыха',
                'image': 'https://images.unsplash.com/photo-1556906781-9a412961c28c?w=600&h=400&fit=crop'
            },
            {
                'title': 'HomeComfort',
                'bio': 'Товары для дома и сада',
                'image': 'https://images.unsplash.com/photo-1556912173-46c336c7fd55?w=600&h=400&fit=crop'
            }
        ]
        
        shops = []
        for idx, data in enumerate(shop_data, start=1):
            # Создаем или получаем пользователя-продавца
            email = f'seller{idx}@example.com'
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'Продавец{idx}',
                    'last_name': f'Магазин{idx}',
                    'role': User.RoleChoices.SELLER
                }
            )
            
            if user_created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  → Создан пользователь: {email}')
            
            # Создаем или получаем магазин
            shop, shop_created = Shop.objects.get_or_create(
                title=data['title'],
                defaults={
                    'seller': user,
                    'bio': data['bio'],
                    'is_deleted': False
                }
            )
            
            if shop_created or not shop.avatar:
                # Загружаем изображение для магазина
                image_file = self.download_image(data['image'], 600, 400)
                shop.avatar.save(f'{data["title"].lower()}.jpg', image_file, save=True)
                self.stdout.write(f'  → Создан магазин: {data["title"]}')
            else:
                self.stdout.write(f'  → Магазин уже существует: {data["title"]}')
            
            shops.append(shop)
        
        return shops

    def create_products(self, categories, shops):
        """Создает 20 продуктов с изображениями"""
        product_templates = [
            {
                'title': 'Смартфон Galaxy X',
                'description': 'Современный смартфон с отличной камерой',
                'price': 45000,
                'category_idx': 0,
                'images': [
                    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1592286927505-b0501739c61b?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Ноутбук ProBook',
                'description': 'Мощный ноутбук для работы и игр',
                'price': 85000,
                'category_idx': 0,
                'images': [
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Наушники Wireless',
                'description': 'Беспроводные наушники с шумоподавлением',
                'price': 12000,
                'category_idx': 0,
                'images': [
                    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1545127398-14699f92334b?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Планшет TabPro',
                'description': 'Легкий планшет для учебы и развлечений',
                'price': 35000,
                'category_idx': 0,
                'images': [
                    'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1585790050230-5dd28404f905?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Джинсы классические',
                'description': 'Удобные джинсы из качественного денима',
                'price': 3500,
                'category_idx': 1,
                'images': [
                    'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1604176354204-9268737828e4?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Футболка хлопковая',
                'description': 'Мягкая футболка из 100% хлопка',
                'price': 1200,
                'category_idx': 1,
                'images': [
                    'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Куртка зимняя',
                'description': 'Теплая куртка для холодной погоды',
                'price': 8500,
                'category_idx': 1,
                'images': [
                    'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Кроссовки спортивные',
                'description': 'Легкие кроссовки для бега',
                'price': 5500,
                'category_idx': 1,
                'images': [
                    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Роман "Мастер и Маргарита"',
                'description': 'Классика русской литературы',
                'price': 650,
                'category_idx': 2,
                'images': [
                    'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Учебник Python',
                'description': 'Полное руководство по программированию',
                'price': 1800,
                'category_idx': 2,
                'images': [
                    'https://images.unsplash.com/photo-1589998059171-988d887df646?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Детектив "Убийство в Восточном экспрессе"',
                'description': 'Захватывающий детектив Агаты Кристи',
                'price': 550,
                'category_idx': 2,
                'images': [
                    'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Гантели 10 кг',
                'description': 'Набор гантелей для домашних тренировок',
                'price': 2500,
                'category_idx': 3,
                'images': [
                    'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Коврик для йоги',
                'description': 'Нескользящий коврик для занятий йогой',
                'price': 1500,
                'category_idx': 3,
                'images': [
                    'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1592432678016-e910b452f9a2?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Велосипед горный',
                'description': 'Прочный велосипед для бездорожья',
                'price': 35000,
                'category_idx': 3,
                'images': [
                    'https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1571333250630-f0230c320b6d?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Мяч футбольный',
                'description': 'Профессиональный футбольный мяч',
                'price': 2200,
                'category_idx': 3,
                'images': [
                    'https://images.unsplash.com/photo-1614632537423-1e6c2e7e0aae?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Набор инструментов',
                'description': 'Универсальный набор для дома',
                'price': 4500,
                'category_idx': 4,
                'images': [
                    'https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Газонокосилка электрическая',
                'description': 'Мощная газонокосилка для сада',
                'price': 15000,
                'category_idx': 4,
                'images': [
                    'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Лейка садовая',
                'description': 'Удобная лейка на 10 литров',
                'price': 450,
                'category_idx': 4,
                'images': [
                    'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Крем для лица',
                'description': 'Увлажняющий крем с витаминами',
                'price': 1200,
                'category_idx': 5,
                'images': [
                    'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&h=600&fit=crop'
                ]
            },
            {
                'title': 'Шампунь органический',
                'description': 'Натуральный шампунь без сульфатов',
                'price': 850,
                'category_idx': 5,
                'images': [
                    'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=800&h=600&fit=crop',
                    'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800&h=600&fit=crop'
                ]
            },
        ]
        
        products = []
        for template in product_templates:
            category = categories[template['category_idx']]
            shop = random.choice(shops)
            
            # Создаем или получаем продукт
            product, created = Product.objects.get_or_create(
                title=template['title'],
                shop=shop,
                defaults={
                    'description': template['description'],
                    'price': template['price'],
                    'quantity': random.randint(5, 100),
                    'discount': random.choice([None, 5, 10, 15, 20]),
                    'category': category,
                    'is_deleted': False,
                    'views_count': random.randint(0, 500)
                }
            )
            
            if created:
                # Создаем изображения продукта
                for idx, image_url in enumerate(template['images']):
                    is_main = (idx == 0)
                    image_file = self.download_image(image_url, 800, 600)
                    
                    image_obj = ImageProduct.objects.create(
                        product=product,
                        is_main_image=is_main
                    )
                    image_obj.image.save(
                        f'{template["title"].lower().replace(" ", "_")}_{idx}.jpg',
                        image_file,
                        save=True
                    )
                
                self.stdout.write(f'  → Создан продукт: {template["title"]} (магазин: {shop.title})')
            else:
                self.stdout.write(f'  → Продукт уже существует: {template["title"]}')
            
            products.append(product)
        
        return products
