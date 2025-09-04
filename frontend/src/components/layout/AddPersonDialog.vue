<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod";
import * as z from "zod";

// --- 导入 ElMessage ---
import { ElMessage } from 'element-plus';
// ----------------------

// 导入 Vee-Validate 的相关类型
import type { SubmissionHandler } from 'vee-validate';

// 从 shadcn-vue 导入 UI 组件 (保留不变)
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

// --- 导入 Pinia store ---
import { useUsersStore } from '@/store/usersStore.ts';
const userStore = useUsersStore();
// -----------------------

// 定义原始的 Zod schema 对象 (保留不变)
const rawPersonSchema = z.object({
  username: z
      .string()
      .min(2, "用户名最少2个字符")
      .max(50, "用户名最多50个字符")
      .nonempty("用户名不能为空"),
  phone: z
      .string()
      .regex(/^1[3-9]\d{9}$/, "请输入有效的11位手机号")
      .nonempty("手机号不能为空"),
  password: z
      .string()
      .min(8, "密码最少8个字符")
      .max(20, "密码最多20个字符")
      .nonempty("密码不能为空"),
});

// 将原始 Zod schema 转换为 VeeValidate 兼容的 TypedSchema (保留不变)
const personSchema = toTypedSchema(rawPersonSchema);

const onSubmit: SubmissionHandler = async (values, actions) => {
  try {
    // 这里 values 的类型会是 any，但我们可以用 Zod 来验证
    const validatedValues = rawPersonSchema.parse(values);

    // 确保 values 传递给 store action 时是正确类型
    const newUser = await userStore.addUser(validatedValues);

    // --- 替换为 ElMessage.success ---
    ElMessage.success({
      message: `人员 ${newUser.username} 添加成功！`
    });
    // ---------------------------------

    // 成功后重置表单
    actions.resetForm();

  } catch (error: any) {
    // --- 替换为 ElMessage.error ---
    console.error("添加人员失败:", error); // 打印错误到控制台进行调试
    throw error;

  }
};
</script>

<template>
  <Form v-slot="{ handleSubmit }" as="" keep-values :validation-schema="personSchema">
    <Dialog>
      <DialogTrigger as-child>
        <Button variant="outline">
          添加人员
        </Button>
      </DialogTrigger>
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>添加新人员</DialogTitle>
          <DialogDescription>
            请填写新人员的用户名、手机号和密码。
          </DialogDescription>
        </DialogHeader>

        <form id="addPersonForm" @submit="handleSubmit($event, onSubmit)">
          <!-- 用户名字段 -->
          <FormField v-slot="{ componentField }" name="username">
            <FormItem class="mb-4">
              <FormLabel>用户名</FormLabel>
              <FormControl>
                <Input type="text" placeholder="请输入用户名" v-bind="componentField" />
              </FormControl>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>

          <!-- 手机号字段 -->
          <FormField v-slot="{ componentField }" name="phone">
            <FormItem class="mb-4">
              <FormLabel>手机号</FormLabel>
              <FormControl>
                <Input type="tel" placeholder="请输入11位手机号" v-bind="componentField" />
              </FormControl>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>

          <!-- 密码字段 -->
          <FormField v-slot="{ componentField }" name="password">
            <FormItem class="mb-6">
              <FormLabel>密码</FormLabel>
              <FormControl>
                <Input type="password" placeholder="请输入密码" v-bind="componentField" />
              </FormControl>
              <FormMessage class="mt-1" />
            </FormItem>
          </FormField>
        </form>

        <DialogFooter>
          <Button type="submit" form="addPersonForm">
            确定
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Form>
</template>